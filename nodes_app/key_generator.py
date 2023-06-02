# key_generator.py
import hashlib
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class DeterministicRNG:
    def __init__(self, seed):
        self.generator = hashlib.sha256(seed).digest()

    def getrandbits(self, n):
        random_bits = bytearray()
        while len(random_bits) * 8 < n:
            self.generator = hashlib.sha256(self.generator).digest()
            random_bits.extend(self.generator)
        bits_int = int.from_bytes(random_bits, byteorder='big', signed=False)
        return bits_int & ((1 << n) - 1)

def generate_key_pair(data):
    # Asegurar que la generación de claves siempre genere el mismo resultado
    private_key_salt = hashlib.sha256(data.encode()).digest()
    deterministic_rng = DeterministicRNG(private_key_salt)

    # Generar clave privada basada en el 'private_key_salt' como un número aleatorio
    private_key = RSA.generate(2048, e=65537, randfunc=deterministic_rng.getrandbits)

    # Generar la clave pública correspondiente
    public_key = private_key.publickey()

    # Convertir las claves a objetos compatibles con cryptography
    private_key_numbers = private_key.export_key(format='DER')
    public_key_numbers = public_key.export_key(format='DER')

    private_key = serialization.load_der_private_key(private_key_numbers, None, default_backend())
    public_key = serialization.load_der_public_key(public_key_numbers, default_backend())

    # Serializar la clave privada y la clave pública
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem
