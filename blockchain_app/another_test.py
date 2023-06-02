from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import base64
import hashlib

def hybrid_encrypt(public_key_pem, message):
    # Generar una clave AES aleatoria
    aes_key = get_random_bytes(32)

    # Cifrar el mensaje con la clave AES
    cipher_aes = AES.new(aes_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(message.encode())

    # Cifrar la clave AES con la clave pública RSA
    public_key = RSA.import_key(public_key_pem)
    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)

    # Devolver la clave AES cifrada, el nonce de AES, el tag de AES y el texto cifrado
    # Todos estos son necesarios para descifrar el mensaje
    return base64.b64encode(encrypted_aes_key + cipher_aes.nonce + tag + ciphertext)

def hybrid_decrypt(private_key_pem, encrypted_message, passphrase):
    # Convertir el mensaje de base64 a bytes
    encrypted_message = base64.b64decode(encrypted_message)

    # Extraer la clave AES cifrada, el nonce de AES, el tag de AES y el texto cifrado
    encrypted_aes_key = encrypted_message[:256]
    nonce = encrypted_message[256:272]
    tag = encrypted_message[272:288]
    ciphertext = encrypted_message[288:]

    # Descifrar la clave AES con la clave privada RSA
    private_key = RSA.import_key(private_key_pem, passphrase=passphrase)
    cipher_rsa = PKCS1_OAEP.new(private_key)
    aes_key = cipher_rsa.decrypt(encrypted_aes_key)

    # Descifrar el mensaje con la clave AES
    cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
    message = cipher_aes.decrypt_and_verify(ciphertext, tag)

    return message.decode()  # Devolver el mensaje descifrado como una cadena


def generate(pk, username, user_id, vote):
    #concatenar los valores en una cadena
    data = f"{pk}{user_id}{username}{vote}"
    
    private_key, public_key = deterministic_rsa_key_generation(data)

    # Exportar las claves privada y pública
    secret_code = "info_to"
    private_pem = private_key.export_key(passphrase=secret_code)
    public_pem = public_key.export_key()

    print('private_pem',private_pem)
    print('public_pem',public_pem)
    return (private_pem, public_pem)        

def deterministic_rsa_key_generation(data):
    # Asegurar que la generación de claves siempre genere el mismo resultado
    private_key_salt = hashlib.sha256(data.encode()).digest()

    # Generar un entero pseudoaleatorio basado en el 'private_key_salt'
    key_size = 1024 #2048
    exponent = 257 #65537
    deterministic_rng = int.from_bytes(private_key_salt, byteorder='big') % (1 << (key_size - 1))

    # Generar la clave privada basada en el entero pseudoaleatorio
    try:
        private_key = RSA.construct((deterministic_rng, exponent))
    except ValueError:
        return deterministic_rsa_key_generation(data + "0")

    # Generar la clave pública correspondiente
    public_key = private_key.publickey()

    return private_key, public_key

private_key_pem, public_key_pem = generate(1, 'yo', '12345', '1')

# Encriptar un mensaje con la clave pública
encrypted_message = hybrid_encrypt(public_key_pem, "se")

# Descifrar el mensaje con la clave privada
decrypted_message = hybrid_decrypt(private_key_pem, encrypted_message, "info_to")
print(decrypted_message)  # Debería imprimir: "Este es un mensaje secreto"