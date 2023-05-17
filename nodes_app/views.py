from django.shortcuts import render
from django.http import HttpResponse

import hashlib
# import rsa
from django.contrib.auth.models import User
from .models import Node
from uuid import uuid4
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from .key_generator import generate_key_pair

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util import number


def index(request):
    return HttpResponse('Hola mundo con nodes')

class Nodes:

    def __init__(self) -> None:
        pass

    def create_node(self, ip_address, net_address, location, processing_capacity, user):
        #se crea un id aleatorio
        node_id = str(uuid4()).replace('-','')
        node = Node.objects.create(node_id=node_id, ip_address=ip_address
                                   ,net_address=net_address, location=location
                                   ,processing_capacity=processing_capacity, user=user)
        node.save()
        return node
    
    def update_node(self, user, node, net_address, location, processing_capacity, password):
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
            key_gen = KeyGeneration()
            pp_key = key_gen.generate(node.node_id, node.net_address, password)
            node.private_key = pp_key[0]
            node.public_key = pp_key[1]
            node.save()
            response = {'message': 'Se ha actualizado la información.'}
        else:
            #si no coinciden, se debe retornar el error o advertencia sobre la contraseña erronea
            response = {'message': 'La constraseña ingresada no coincide con la contraseña de la cuenta.'}
        #se guarda
        return JsonResponse(response)
    
    

class KeyGeneration():
    """
    Esta clase no se exporta ni se muestra a nadie, queda dentro de la lógica interna del nodo 
    y se lanza automáticamente cuando el nodo es invocado
    """
    def __init__(self) -> None:
        pass

    def generate(self, node_id, net_address, password):
        #concatenar los valores en una cadena
        #data = f"{node_id}{password}"
        data = f"{node_id}{net_address}{password}"
        print(data)
        #Obtener el hash SHA-256 de la cadena anterior:
        #forma 1
        # hash = hashlib.sha256(data.encode()).hexdigest()
        # #Generar las claves pública y privada utilizando el módulo rsa. Para ello, se utiliza el hash SHA-256 como semilla para la generación de las claves:
        # #En este caso, se están generando claves de 512 bits de longitud, utilizando un tamaño de pool de 8 bits y un valor de e de 65537.
        # (private_key, public_key) = rsa.newkeys(512, poolsize=8, hash_func=hash, randfunc=rsa.randnum.read_random_bits, e=65537)
        # #Para almacenar las claves en la base de datos, se convierten a strings y se guardan en los modelos correspondientes
        # private_key_str = private_key.save_pkcs1().decode()
        # public_key_str = public_key.save_pkcs1().decode()

        #forma 2        
        # # Generar el par de claves RSA de 2048 bits
        # key = rsa.generate_private_key(public_exponent=65537, key_size=2048, numbers=rsa.RSAPublicNumbers.from_seed(data))
        # print('key: ' + key)
        # # Serializar la clave privada y guardarla como cadena de caracteres
        # private_key = key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption()).decode('utf-8')        
        # # Serializar la clave pública y guardarla como cadena de caracteres
        # public_key = key.public_key().public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
        # print(private_key, public_key)

        # # forma 3 -> module 'lib' has no attribute 'RSA_generate_key'
        # # Asegurar que la generación de claves siempre genere el mismo resultado
        # private_key_salt = hashlib.sha256(data.encode()).digest()
        # # Generar clave privada basada en el 'private_key_salt' como un número aleatorio
        # private_key_cdata = backend._lib.RSA_generate_key(2048, 65537, backend._ffi.NULL, private_key_salt)
        # private_key = _RSAPrivateKey(backend, private_key_cdata)
        #  # Generar la clave pública correspondiente
        # public_key = private_key.public_key()
        # # Serializar la clave privada y la clave pública
        # private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption())
        # public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
        # # return private_pem, public_pem

        # #forma 4
        # # key_generator.py
        # private_key_pem, public_key_pem = generate_key_pair(data)
        # response_data = {
        # 'private_key': private_key_pem.decode(),
        # 'public_key': public_key_pem.decode()
        # }
        # return JsonResponse(response_data)
        
        # #forma 5 de stack overflow
        # ############ GENERACIÓN DE LA CLAVE ###############
        # # Generar pareja de claves RSA de 2048 bits de longitud
        # key = RSA.generate(2048)
        # # Passphrase para encriptar la clave privada
        # secret_code = data
        # # Exportamos la clave privada
        # private_key = key.export_key(passphrase=secret_code)
        # # Guardamos la clave privada en un fichero
        # print(private_key)
        # print(dir(private_key))
        # # with open("private.pem", "wb") as f:
        # #     f.write(private_key)
        # # Obtenemos la clave pública
        # public_key = key.publickey().export_key()
        # print(public_key)
        # print(dir(public_key))
        # # # Guardamos la clave pública en otro fichero
        # # with open("public.pem", "wb") as f:
        # #     f.write(public_key)
        # ############ CIFRADO ############### https://es.stackoverflow.com/questions/162038/c%c3%b3mo-puedo-crear-una-llave-p%c3%bablica-y-otra-privada-con-rsa-pycryptodome

        #forma 5 mejorada la 5 con IA
        private_key, public_key = deterministic_rsa_key_generation(data)

        # Exportar las claves privada y pública
        secret_code = "12345"
        private_pem = private_key.export_key(passphrase=secret_code)
        public_pem = public_key.export_key()

        return (private_pem, public_pem)

        # return (private_key, public_key)
        

def deterministic_rsa_key_generation(data):
    # Asegurar que la generación de claves siempre genere el mismo resultado
    private_key_salt = hashlib.sha256(data.encode()).digest()

    # Generar un entero pseudoaleatorio basado en el 'private_key_salt'
    key_size = 2048
    exponent = 65537
    deterministic_rng = int.from_bytes(private_key_salt, byteorder='big') % (1 << (key_size - 1))

    # Generar la clave privada basada en el entero pseudoaleatorio
    try:
        private_key = RSA.construct((deterministic_rng, exponent))
    except ValueError:
        return deterministic_rsa_key_generation(data + "0")

    # Generar la clave pública correspondiente
    public_key = private_key.publickey()

    return private_key, public_key

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

