from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import hashlib
from Crypto import Random

def encrypt_with_public_key(public_key_pem, message):
    # Importar la clave pública
    public_key = RSA.import_key(public_key_pem)

    # Crear un objeto de cifrado
    cipher = PKCS1_OAEP.new(public_key)

    # Convertir el mensaje a bytes y cifrar
    encrypted_message = cipher.encrypt(message.encode())
    print('encrypted_message',encrypted_message)

    return base64.b64encode(encrypted_message)  # Devuelve el mensaje cifrado como una cadena base64

def decrypt_with_private_key(private_key_pem, encrypted_message, passphrase):
    # Importar la clave privada
    private_key = RSA.import_key(private_key_pem, passphrase=passphrase)

    # Crear un objeto de descifrado
    cipher = PKCS1_OAEP.new(private_key)
    
    # Descifrar el mensaje
    decrypted_message = cipher.decrypt(base64.b64decode(encrypted_message))

    return decrypted_message.decode()  # Devuelve el mensaje descifrado como una cadena

def generate(pk, username, user_id, vote):
    key_size = 2048  # tamaño de la clave en bits

    # Generar un par de claves RSA
    private_key = RSA.generate(key_size)
    public_key = private_key.publickey()

    # Exportar las claves privada y pública
    secret_code = "info_to"
    private_pem = private_key.export_key(passphrase=secret_code)
    public_pem = public_key.export_key()

    return private_pem, public_pem      

private_key_pem, public_key_pem = generate('1', 'yo', '12345', '1')
print('private_key_pem',private_key_pem)
print('public_key_pem',public_key_pem)

print('private_key_pem',len(private_key_pem))
print('public_key_pem',len(public_key_pem))

# Encriptar un mensaje con la clave pública
encrypted_message = encrypt_with_public_key(public_key_pem, "se encripta el mensaje y también se decripta, vamos a testear la longitud de esta vuelta")

# Descifrar el mensaje con la clave privada
decrypted_message = decrypt_with_private_key(private_key_pem, encrypted_message, "info_to")
print(decrypted_message)  # Debería imprimir: "Este es un mensaje secreto"
