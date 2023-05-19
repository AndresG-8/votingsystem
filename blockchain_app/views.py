from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

from .models import Chain, Block, Transaction
from django.core import serializers

import hashlib
import json
from datetime import datetime

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import hashlib

def index(request):
    return HttpResponse('Hola mundo con blockchain')

class Blockchain:
    """Cuando se inicia el proceso electoral, se crea la cadena,
    tambien se crea un bloque, este bloque se
    agrega a la cadena, y este id de la cadena es el que se agrega al id 
    de la votación"""
    """Para crear un bloque se requiere crear una transacción, si se desea que el bloque génesis
    tenga cierta información, sería más cómodo crear la transacción, agregarle la info
    y posterior agregar la transacción al bloque y este bloque sería el bloque génesis"""
    def __init__(self, commission_id):
        """se inicializa la cadena de bloques y las transacciones, como esta en bd, no es necesario"""
        if commission_id == 0:
            self.chain = 1
        else:
            try:
                self.chain = Chain.objects.get(votation_id=commission_id) 
            except Chain.DoesNotExist():
                self.chain = 1
        # self.chain = [Block(0, "Genesis Block", "0", 0, "")]
        #acá se debe verificar si hay proceso electoral en proceso o si se va a crear uno
        #tambíen se podrían verificar los nodos y la integridad de la cadena como tal
                     
    def create_genesis(self, votation, user):      
        """Crear cadena"""
        chain = Chain.objects.create(votation=votation)
        chain.save()

        """Crear bloque génesis"""
        #al crear el bloque, se liga de una vez a la cadena de bloques que recien se creó.
        block = self.create_block(nonce=1, previous_hash='0')
        
        print('blockchain_app.views.py-50::información del bloque después de la creación: ', block)

        """Crear transacción génesis"""
        #al agregar la transacción se retorna el número del bloque al cual será agregado, como esto es genesis, no es tan necesario
        sender_signature = 'que buena pregunta' # (¿encriptar admin que crea transacción?)
        trx_data = 'Transacción en el bloque génesis'
        node_id = 'administrador' + user.username
        trx = self.add_transaction(sender=user, sender_signature=sender_signature, trx_data=trx_data, node_id=node_id, block=block)

        """Actualizar el hash al bloque creado con base en la info del bloque y los ids de las transacciones"""
        #se obtienen todas las transacciones del bloque
        trx_list = Transaction.objects.filter(block=block)
        
        block.data = self.hash_data(trx_list)
        #guardar en data el hash de las transacciones permite saber si las transacciones agregadas al bloque corresponden al mismo o no
        #en caso tal de que se quiera validar la pertenencia de una transacción a un bloque
        block.save()

        return block

    def hash_data(self, trx_list):
        #se serializan o convierten las transacciones en json
        #se hashea la información de las transacciones
        return self.hash(serializers.serialize('json', trx_list))

    def create_block(self, nonce, previous_hash, data):
        """Crea un bloque de acuerdo a los datos recibidos"""
        #se crea el bloque con la información que se recibe
        print('blockchain_app.views.py-78::\nVa a crear el bloque')
        block = Block.objects.create(
            index = self.get_last_index_block()+1,
            nonce = nonce,
            previous_hash = previous_hash,
            data = data,
            chain = self.chain
            )
        #algo importante por acá, los nodos si deberían tener firma, por ende cuando se cree un bloque, se debería firmar por un nodo, o no?
        block.save()
        print(f'blockchain_app.views.py-85::\nBloque {block.index} creado')
        return block
    
    def get_last_index_block(self):
        """
        Obtiene el indice del último bloque creado ->debe pertenencer a la cadena de bloques indicada
        """
        try:
            block = Block.objects.filter(chain_id=self.chain.id).latest('index')
            block_index = block.index
        except Block.DoesNotExist:
            block_index = 1

        return block_index

    def get_last_block(self):
        """
        Obtiene el último bloque creado ->debe pertenencer a la cadena de bloques indicada
        """
        try:
            block = Block.objects.filter(chain_id=self.chain.id).latest('index')
        except Block.DoesNotExist:
            block = None

        return block
    
    def add_transaction(self, sender, sender_signature, trx_data, node_id, block):
        """
        Agrega una transacción a la cadena de bloques y retorna el bloque en el cual se asigna (el retorno acá no es muy diciente)
        """
        transaction = Transaction.objects.create(sender=sender, sender_signature=sender_signature, trx_data=trx_data, node_id=node_id, block=block)
        transaction.save()
        return block.index
    
    @staticmethod
    def hash(data):
        """
        Hashea el dato/bloque recibido. Primero lo pasa a JSON, codifica en bytes y luego lo hashea
        """
        #se codifica la información en formato json y se ordena alfabéticamente
        encoded_data = json.dumps(data, sort_keys = True).encode()
        #luego se retorna el hash del json
        return hashlib.sha256(encoded_data).hexdigest()

    ############voy revisando y corrigiendo por acá
    #la prueba de trabajo consiste en encontrar un hash que termine en 4 ceros usando el nonce enviado anteriormente y el nuevo nonce
    def proof_of_work(self, previous_nonce):
        new_nonce = 1
        check_nonce = False
        while check_nonce is False:
            hash_operation = hashlib.sha256(str(new_nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_nonce = True
            else:
                new_nonce += 1
        #el nonce (número usado solo una vez) es el número que queda después de realizar la prueba de trabajo
        return new_nonce
    
    def is_chain_valid(self):
        """
        Verifica si la cadena es correcta -> por definir lógica respecto a base de datos
        """
        #Recorre toda la cadena de bloques
        for i in range(1, len(self.chain)):
            #obtiene la información del bloque actual
            current_block = self.chain[i]
            #obtiene la información del bloque anterior
            previous_block = self.chain[i - 1]
            #compara el hash de ambos bloques, si son diferentes, la cadena no es válida
            if current_block.previous_hash != previous_block.hash_block():
                return False
            #valida además que el bloque tenga información correcta y validada (?)
            if not self.validate_block(current_block):
                return False

        return True


#     def is_valid(self):
#         """
#         Verifica si el bloque es válido.
#         """
#         block_data = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}{self.nonce}"
#         hash_object = hashlib.sha256(block_data.encode())
#         if self.hash != hash_object.hexdigest():
#             return False
#         if self.index > 0:
#             previous_block = Block.objects.get(index=self.index - 1)
#             if self.previous_hash != previous_block.hash:
#                 return False
#         return True

#     def validate_block(self, block):
#         # validar la firma digital del bloque utilizando la clave pública del nodo validador correspondiente
#         # Devolver True si la firma es válida, de lo contrario devolver False.
#         pass

#     def generate_hash(self): falta crear la prueba de trabajo acá
#         """
#         Genera el hash del bloque utilizando la prueba de trabajo.
#         """
#         while not self.hash.startswith('00'):
#             self.nonce += 1
#             block_data = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}{self.nonce}"
#             hash_object = hashlib.sha256(block_data.encode())
#             self.hash = hash_object.hexdigest()


    # def add_node(self, address):
    #     parsed_url = urlparse(address)
    #     self.nodes.add(parsed_url.netloc)

    # #itera por cada nodo conectado a ver cual tiene la cadena mas larga y se valida, posteriormente retorna la cadena mas larga y esta será la real
    # def replace_chain(self):
    #     network = self.nodes
    #     longest_chain = None
    #     max_length = len(self.chain)
    #     for node in network:
    #         #acá me queda la duda con el request -> en el ejemplo es requests
    #         #obtiene la cadena de ese nodo específico -> esta usando una peticion a la url (estilo API)
    #         response = requests.get(f'http://{node}/get_chain')
    #         if response.status_code == 200:
    #             length = response.json()['length']
    #             chain = response.json()['chain']
    #             if length > max_length and self.is_chain_valid(chain):
    #                 max_length = length
    #                 longest_chain = chain
    #     if longest_chain:
    #         self.chain = longest_chain
    #         return True
    #     return False  
