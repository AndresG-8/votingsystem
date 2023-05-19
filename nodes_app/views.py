from django.shortcuts import render
from django.http import HttpResponse

import hashlib
# import rsa
from django.contrib.auth.models import User, Group
from .models import Node
from uuid import uuid4
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse

import blockchain_app.keys as keys
from blockchain_app.views import Blockchain
from mempool_app.views import Mempool

from blockchain_app.models import Transaction
from users_app.models import UserDetail

import json

def index(request):
    return HttpResponse('Hola mundo con nodes')

class Nodes:

    def __init__(self) -> None:
        #acá se podría validar que quien invoque esta clase sea un nodo registrado
        pass

    @staticmethod
    def create_node(ip_address, net_address, location, processing_capacity, user):
        #se crea un id aleatorio
        node_id = str(uuid4()).replace('-','')
        node = Node.objects.create(node_id=node_id, ip_address=ip_address
                                   ,net_address=net_address, location=location
                                   ,processing_capacity=processing_capacity, user=user)
        node.save()
        return node
    
    @staticmethod
    def update_node(user, node, net_address, location, processing_capacity, password):
        #se busca el nodo con base en la información que se obtiene de la vista de vote
        node = Node.objects.get(id=node.id)
        #luego que se obtiene el nodo, se modifican los atributos
        node.net_address = net_address
        node.location = location
        node.processing_capacity = processing_capacity
        # user = User.objects.get(pk=user.id) ->ps si ya lo mandaron por parametros, para que volver a buscarlo?

        #luego se debe comprobar que la contraseña es la misma del usuario -> para esto se debe encriptar de la misma manera en como se encripta la contraseña del usuario
        if check_password(password, user.password):
            #si coinciden, se procede a crear el par de llaves
            (private_key_pem, public_key_pem) = keys.generate()
            node.private_key = f"{private_key_pem.decode('UTF-8')}"
            node.public_key = f"{public_key_pem.decode('UTF-8')}"
            node.save()
            response = {'status':'ok', 'message': 'Se ha actualizado la información.'}
        else:
            #si no coinciden, se debe retornar el error o advertencia sobre la contraseña erronea
            response = {'status':'ok', 'message': 'La contraseña ingresada no coincide con la contraseña de la cuenta.'}
        #se guarda
        return JsonResponse(response)
    
    @staticmethod
    def get_nodes():
        return Node.objects.filter(active=True)

    def mine(user_id, commission_id, quantity):
        """
        Minar las transacciones: recibe el user_id, el id de la votación y la cantidad de transacciones a minar.
        Retorna JsonResponse con status y message.
        """
        ## commission = get_object_or_404(Votation, pk=commission_id) #este se puso para validar que si exista esa votación
        
        #debe tomar las transacciones disponibles de la mempool que son de la votación seleccionada
        node = Node.objects.get(user_id=user_id)
        #nota: quitar la cantidad de acá para que queden por defecto
        mempool_trx = Mempool.get_related_mem_trx(related_votation=commission_id, quantity=quantity)
        
        if not mempool_trx.exists():
            return JsonResponse({'status':'error', 'message':'¡No hay transacciones que puedan ser minadas para la votación seleccionada!'})
        
        #una vez se han seleccionado las transacciones, se bloquean y se les asigna el nodo_id
        for mem_trx in mempool_trx:
            Mempool.update_status(mem_trx.id, node.node_id)
        
        #crear el objeto blockchain con la información de la comision
        blockchain = Blockchain(commission_id)
        
        #obtener el último bloque de la cadena
        last_block = blockchain.get_last_block()

        dict_block = {'block_index':last_block.index,
                      'block_data': {'block_id':last_block.id,
                                     'block__index':last_block.index,
                                     'block_timestamp':str(last_block.timestamp),
                                     'block_previous_hash':last_block.previous_hash,
                                     'block_nonce':last_block.nonce,
                                     'block_chain':last_block.chain.id,
                                     }
                      }
        print(f'nodes_app.viewa.py-87::\nBloque que se debe hashear\n{dict_block}')
        
        last_block_hashed = blockchain.hash(dict_block)
        
        #hacer prueba de trabajo, se le envia el nonce del bloque anterior -> la prueba de trabajo deben ser las validaciones de autenticidad
        new_nonce = blockchain.proof_of_work(previous_nonce=last_block.nonce)
        
        #retomar el listado de transacciones bloqueadas por el nodo explicitamente
        taken_memtrx = Mempool.get_taken_trx(commission_id, node.node_id)

        #hashear las transacciones de la mempool para agregarlas a la data del bloque
        #el hash_data recibe un listado, lo convierte en json y lo hashea
        data_hashed = blockchain.hash_data(taken_memtrx)
        
        #crear el bloque, esto me retorna el bloque recien creado ->al crear el objeto se liga la cadena al objeto que se esta creando acá
        new_block = blockchain.create_block(nonce=new_nonce, previous_hash=last_block_hashed, data=data_hashed)
        
        #una vez creado el bloque, se le agregan las transacciones que se tomaron
        for trx in taken_memtrx: 
            #Toca corregir como se ve la transacción en el modelo===================================================
            trx_in_block = blockchain.add_transaction(sender=trx.sender, sender_signature=trx.sender_signature, 
                                                      trx_data=trx.trx_data, node_id=node.node_id, block=new_block)
            
            print(f'nodes_app.views.py-107::\nLa transacción {trx.id} se agrega al bloque {trx_in_block}')
            #y como ya este nodo creo el bloque, se eliminan de la mempool
            Mempool.delete_trx(trx_id=trx.id)

        return JsonResponse({'status':'ok', 'message':'¡Se ha minado correctamente el bloque!'})

    @staticmethod
    def count_votes(commission_id):
        """
        Cada candidato debe tomar TODAS las transacciones de la blockchain y validar que si sea un voto para él
        por ahora pondré todo genérico y por cada uno de los candidatos, que se haga el proceso.
        """
        total_votes = 0
        #Tomar cada uno de los candidatos
        group = Group.objects.get(name='candidates')
        users = group.user_set.all()
        #Recorrer por cada usuario, TODAS las transacciones
        for candidate in users:
            if candidate.userdetail.is_candidate:
                cup_key = candidate.userprofile.private_key
                #Tomar todas las transacciones de la base de datos correspondientes a la votación
                trxs = Transaction.objects.all()
                #Defino una variable de contador de votos
                vote_counter = 0
                #por cada transacción, el usuario intentará descifrar el contenido de trx_data
                for trx in trxs:                
                    decrypted_trx = keys.decrypt_with_private_key(cup_key, trx.trx_data, "se_podria_cambiar")
                    str_decrypted_trx = decrypted_trx.content
                    data_decrypted_trx = json.loads(str_decrypted_trx)
                    status = data_decrypted_trx['status']
                    message = data_decrypted_trx['message']
                    if status != 'ok':
                        if message.find('Incorrect decryption') != -1:
                            print(f'error descrifrando para {candidate.username} error: {message}')
                        else:
                            print(f'otro tipo de error a controlar {candidate.username} error: {message}')
                    else:
                        vote_counter += 1
                        print(f'transaccion para {candidate.username}', decrypted_trx)
                        # candidate.userdetail.votes_received += 1
                        # candidate.save()
                #finalizada la cuenta de votos, se busca el usuario y se le agregan los votos
                print(f'Conteo de votos: {candidate.username} obtiene {vote_counter}')
                user = UserDetail.objects.get(user_id=candidate.id)
                user.votes_received = vote_counter
                total_votes += vote_counter
                print(total_votes)
                user.save()
        #si un usuario puede descrifrarlo, el voto es para él
        #si no puede, simplemente continua sin sumar voto.        
        return JsonResponse({'status':'ok', 'message':'Termina el conteo de votos! '+str(total_votes)+' votos contabilizados en total'})    



# from django.shortcuts import render
# from mempool_app.models import Transaction, Block
# from datetime import datetime
# import hashlib

# def mine(request):
#     transactions = Transaction.objects.all()
#     previous_block = Block.objects.last()
#     previous_hash = previous_block.hash if previous_block else '0'
#     block = Block(index=previous_block.index + 1 if previous_block else 0,
#                   timestamp=datetime.now(),
#                   previous_hash=previous_hash)
#     for transaction in transactions:
#         block.transactions.add(transaction)
#     proof = 1
#     check_proof = False
#     while check_proof is False:
#         hash_operation = hashlib.sha256(str(proof**2 - (proof-1)**2).encode()).hexdigest()
#         if hash_operation[:4] == '0000':
#             check_proof = True
#         else:
#             proof += 1
#     block.nonce = proof
#     block.hash = hashlib.sha256(str(block.index).encode() +
#                                  str(block.timestamp).encode() +
#                                  str(block.transactions).encode() +
#                                  str(block.previous_hash).encode() +
#                                  str(block.nonce).encode()).hexdigest()
#     block.save()
#     transactions.delete()
#     return render(request, 'mine.html', {'block': block})

