from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import hashlib
from Crypto import Random
from django.http import JsonResponse

@staticmethod
def encrypt_with_public_key(public_key_pem, message):
    # Importar la clave pública
    public_key = RSA.import_key(public_key_pem)

    # Crear un objeto de cifrado
    cipher = PKCS1_OAEP.new(public_key)

    # Convertir el mensaje a bytes y cifrar
    encrypted_message = cipher.encrypt(message.encode())

    return base64.b64encode(encrypted_message)  # Devuelve el mensaje cifrado como una cadena base64

def decrypt_with_private_key(private_key_pem, encrypted_message, passphrase):
    try:
        # Importar la clave privada
        private_key = RSA.import_key(private_key_pem, passphrase=passphrase)
    except (ValueError, TypeError) as e:
        return JsonResponse({'status':'error', 'message':'Error al importar la clave privada: '+str(e) })

    try:
        # Crear un objeto de descifrado
        cipher = PKCS1_OAEP.new(private_key)
    except ValueError as e:
        return JsonResponse({'status':'error', 'message':'Error al crear el objeto de descifrado: ' + str(e)})
        
    try:
        # Descifrar el mensaje
        decrypted_message = cipher.decrypt(base64.b64decode(encrypted_message))
    except (ValueError, TypeError) as e:
        return JsonResponse({'status':'error', 'message':'Error al descifrar el mensaje: ' + str(e)})

    try:
        # Devolver el mensaje descifrado # Devuelve el mensaje descifrado como una cadena
        return JsonResponse({'status':'ok', 'message':decrypted_message.decode()})
    except UnicodeDecodeError as e:
        return JsonResponse({'status':'error', 'message':'Error al decodificar el mensaje descifrado: ' + str(e)})

def encrypt_with_private_key(private_key_pem, message, passphrase):
    # Importar la clave privada
    private_key = RSA.import_key(private_key_pem, passphrase=passphrase)

    # Crear un objeto de cifrado
    cipher = PKCS1_OAEP.new(private_key)

    # Convertir el mensaje a bytes y cifrar
    encrypted_message = cipher.encrypt(message.encode())

    return base64.b64encode(encrypted_message)  # Devuelve el mensaje cifrado como una cadena base64

def decrypt_with_public_key(public_key_pem, encrypted_message):
    # Importar la clave pública
    public_key = RSA.import_key(public_key_pem)

    # Crear un objeto de descifrado
    cipher = PKCS1_OAEP.new(public_key)
    
    # Descifrar el mensaje
    decrypted_message = cipher.decrypt(base64.b64decode(encrypted_message))

    return decrypted_message.decode()  # Devuelve el mensaje descifrado como una cadena


def generate():
    key_size = 2048  # tamaño de la clave en bits
    # Generar un par de claves RSA
    private_key = RSA.generate(key_size)
    public_key = private_key.publickey()
    # Exportar las claves privada y pública
    secret_code = "se_podria_cambiar" 
    private_pem = private_key.export_key(passphrase=secret_code)
    public_pem = public_key.export_key()
    return private_pem, public_pem      

# private_key_pem, public_key_pem = generate()
# print('private_key_pem',private_key_pem)
# print('public_key_pem',public_key_pem)

# # Encriptar un mensaje con la clave pública
# encrypted_message = encrypt_with_public_key(public_key_pem, "{'commission_id':'12', 'vote':'1'}")

# # Descifrar el mensaje con la clave privada
# # '1yo12345'
# decrypted_message = decrypt_with_private_key(private_key_pem, encrypted_message, "se_podria_cambiar")
# print(decrypted_message)  # Debería imprimir: "Este es un mensaje secreto"
