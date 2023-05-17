from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import UserProfile
from datetime import datetime
from django.utils import timezone

from uuid import uuid4
import blockchain_app.keys as keys

@receiver(user_logged_in)
def update_first_login(sender, user, request, **kwargs):
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    if created or not user_profile.first_login:
        #crear un id_user aleatorio (no confundir con user_id que es la llave principal de los usuarios en el modelo User)
        user_profile.id_user = str(uuid4()).replace('-','')
        user_profile.first_login = timezone.now()
        #generar el par de claves y guardarlas en la base de datos (neh, no importa donde se guarden por ahora)
        # private_key_pem, public_key_pem = keys.generate(user_profile.user.pk, user_profile.user.username, user_profile.user_id)
        (private_key_pem, public_key_pem) = keys.generate() #retorna una tupla de bytes
        user_profile.private_key = f"{private_key_pem.decode('utf-8')}" #como retorno bytes, se decodifica y se guarda como string
        user_profile.public_key = f"{public_key_pem.decode('utf-8')}"
        user_profile.save()          

#TODO - validar si acá se necesario ponerle datos de perfil a los nodos, creería que no ya que ellos tienen su propia pem y eso