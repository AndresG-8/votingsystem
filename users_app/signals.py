from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import UserProfile
from datetime import datetime
from django.utils import timezone

from Crypto.PublicKey import RSA
import hashlib

from uuid import uuid4

@receiver(user_logged_in)
def update_first_login(sender, user, request, **kwargs):
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    if created or not user_profile.first_login:
        user_profile.id_user = node_id = str(uuid4()).replace('-','')
        user_profile.first_login = timezone.now()
        key_gen = KeyGeneration()
        pp_key = key_gen.generate(user_profile.user.pk, user_profile.user.username, user_profile.user_id, 1)
        user_profile.private_key = pp_key[0]
        user_profile.public_key = pp_key[1]
        user_profile.save()          

class KeyGeneration():
    """
    Esta clase no se exporta ni se muestra a nadie, queda dentro de la lógica interna del nodo 
    y se lanza automáticamente cuando el nodo es invocado
    """
    def __init__(self) -> None:
        pass

    def generate(self, pk, username, user_id, vote):
        #concatenar los valores en una cadena
        data = f"{pk}{user_id}{username}{vote}"
        
        private_key, public_key = deterministic_rsa_key_generation(data)

        # Exportar las claves privada y pública
        secret_code = "info_to_save_in_dot_pem"
        private_pem = private_key.export_key(passphrase=secret_code)
        public_pem = public_key.export_key()

        return (private_pem, public_pem)        

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