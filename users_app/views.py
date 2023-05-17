from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from PIL import Image

from .models import UserDetail, User, UserProfile

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from django.db import IntegrityError

from blockchain_app.views import Blockchain, KeyGeneration
#importación para el formulario
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
import base64
import json

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    elif request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        print(user)
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Usuario y/o contraseña incorrectos.'
            })
        else:
            login(request, user)
            return redirect('home')

@login_required
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm,
        })
    elif request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('home')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'El usuario ya existe.'
                })
        return HttpResponse('Las contraseñas no coinciden.')

@login_required
def signout(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    #obtener los detalles del usuario, si es que está autenticado
    user_detail = None
    propossals = None
    if request.user.is_authenticated:
        try:
            #user_detail = request.user.userdetail
             #se buscan y se carga el objeto del user detail
            # user_detail = UserDetail.objects.filter(user=request.user.id)
            user_detail = UserDetail.objects.get(user=request.user.id)
            #para simplificar el template, se sacan las propuestas por a parte
            propossals = user_detail.propossals
            # print(propossals)
            # for key, value in propossals.items():
            #     print(key, value)
        
        except UserDetail.DoesNotExist:
            messages.info(request, '¡Error consultando la información del usuario!')
    
    if request.method == 'GET':
        return render(request, 'profile.html', {
            'user_in_group': user_in_group(request.user),
            'user_detail' : user_detail,
            'propossals': propossals,
        })
    
    elif request.method == 'POST':       
        #ESTE POST DEBE RETORNAR UN JSON RESPONSE
        #se obtienen los datos ingresados por el usuario
        # data = json.loads(request.body)

        # program_data = data.get('program', '')
        program_data = request.POST['program']
        # profile_image_data = data.get('profile_image', '')
        profile_image_data = request.FILES['profile_image']
        # propossals_data = request.POST['propossalsa']
        data = request.POST
        
        print(f'Program: {program_data} \nProfile Image: {profile_image_data}\Complete Data: {data}')
        
        if profile_image_data:
            #Se extrae la información de la imagen
            # formato, imgstr = profile_image_data.split(';base64,')
            # ext = formato.split('/')[-1]
            # image_data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            # profile_image = request.FILES['profile_image']
            try:
                Image.open(profile_image_data)
            except IOError:
                return JsonResponse({'status': 'error', 'message': 'El archivo ingresado no es una imagen válida.'})
            if profile_image_data.size > 5000000:  # 5MB
                return JsonResponse({'status': 'error', 'message': 'El tamaño de la imagen es superior al permitido, ingresa una imagen de menor tamaño.'})
            
            # mi_modelo.imagen.save(nombre + '.' + ext, data, save=False)
            # user_detail.profile_image.save(request.user.username + '.' + ext, image_data, save=False)
            user_detail.profile_image.save(profile_image_data.name, profile_image_data, save=False)
        
        # data = json.loads(request.body)
        # propossals_data = {k: v for k, v in data.items() if k.startswith('propossals')}
        propossals_data = {k: v for k, v in data.items() if k.startswith('propossals')}
        print(propossals_data)
        if not propossals_data:
            return JsonResponse({'status': 'error', 'message': 'Debe haber al menos una propuesta.'})
        
        for k, v in propossals_data.items():
            if len(v) > 200:
                return JsonResponse({'status': 'error', 'message': 'Una propuesta es demasiado larga.'})
        
        user_detail.propossals = propossals_data

        user_detail.save()

        print('nombre de la imagen cargada: '+user_detail.profile_image.name)
        
        return JsonResponse({'status': 'ok', 'new_image':user_detail.profile_image.name})

        # messages.success(request, '¡Se ha modificado el perfil correctamente!')
        # return render(request, 'profile.html', {
        #     'user_in_group': user_in_group(request.user),
        #     'user_detail' : user_detail,
        #     'propossals': propossals,
        # })
    
#Esta funcion es la misma del home, se podría validar como sacarla a un genérico, o incluso dejarla en el modelo
def user_in_group(user):
    """
    Define a que grupo pertenece el usuario. Se hace de este modo ya que no se sabe
    exactamente a que grupo pertenece el usuario y se debe filtrar por todos para definir cual es
    """
    #se crea un diccionario con los grupos predefinidos, son los relevantes para el proyecto
    groups = {'superadmin':False, 'admins':False, 'candidates':False, 'voters':False, 'nodes':False }
    #se define un diccionario vacío que posteriormente almacenará el grupo al que pertenece el usuario
    active_group = {}
    #se recorre el diccionario predefindido
    for key, value in groups.items():
        #por cada llave, valor del diccionario predefinido, se busca el usuario enviado a que grupo pertenece
        if user.groups.filter(name=key).exists():
            #si se detecta que el usuario pertenece a uno de los grupos, se guarda allí a cual de estos
            active_group[key] = True

    #se retorna el diccionario con el grupo al que pertenece en true
    return active_group


class UserActions:
    
    def voter_vote(self, voter_id, candidate_id, commission_id):
        #2. Cuando un votante desea emitir un voto, cifra su voto utilizando la llave pública del candidato. Además, genera un valor aleatorio, 
        # que se utilizará como prueba de que votó sin revelar por quién votó.
        try:
            voter_profile = UserProfile.objects.get(user_id=voter_id)
        except UserProfile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'El votante no existe en la base de datos.'})
        
        try:
            candidate_profile = UserProfile.objects.get(user_id=candidate_id)
        except UserProfile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'El candidato no existe en la base de datos.'})

        #usar la clase KeyGeneration de la blockchain para cifrar y descifrar
        keygen = KeyGeneration()
        #crear la transacción que se enviará al candidato
        trx_to_encrypt = "{'commission_id':f'{commission_id}', 'vote':'1'}"
        print(trx_to_encrypt)
        #se encripta la transacción con la llave pública del candidato seleccionado
        encypted_trx = keygen.encrypt(trx_to_encrypt, candidate_profile.public_key)
        
        #se crea la firma con base al user_id para firmar la transacción, la firma se debe encriptar con la llave privada del votante
        signature = Blockchain.hash(voter_profile.user_id)
        encrypted_signature = keygen.encrypt(signature, voter_profile.private_key)

        #se crea un diccionario que luego se pasa a json y esto es lo que se retorna
        data_to_return = {'status': 'ok', 
                          'message': {'vuser_id': f'{voter_profile.id_user}', 'cuser_id':f'{candidate_profile.id_user}', 
                          'enc_signature':f'{encrypted_signature}', 'enc_trx':f'{encypted_trx}'}
                          }

        return JsonResponse(data_to_return)

        #como la idea es que no quede registro de quien voto por quien, se cifra el voto pero lo principal de esto no es el voto sino
        #la firma digital del votante, la que se debe validar por los nodos y ahí si emitir el voto

        #se envia el voto encriptado con la llave privada (y otras cosas), fuera se envia el id user normal para que el nodo
        #pueda ingresar a los datos del usuario para revisar su llave pública y validar la información enviada

    def user_has_voted_check(self, user_id):
        """
        Indica que el usuario ha votado
        """
        try:
            userp = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'El candidato no existe en la base de datos.'})
        
        userp.vote = 0
        userp.save()

        return JsonResponse({'status': 'ok', 'message': 'Se ha cambiado el estado del votante.'})

        





        
        

