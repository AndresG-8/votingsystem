from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from django.conf import settings
from django.utils.timezone import make_aware
from datetime import datetime, date, time

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from django.db import IntegrityError
from django.http import JsonResponse

from .models import Votation
from blockchain_app.models import Transaction
from blockchain_app.views import Blockchain
from users_app.models import UserDetail, UserProfile
from users_app.views import UserActions
from mempool_app.views import Mempool
from nodes_app.views import Nodes
from nodes_app.models import Node

from uuid import uuid4
import json

def home(request):
    #se obtiene un listado de las últimas 20 transacciones registradas sin importar de donde son
    latest_transactions_list = Transaction.objects.select_related('block').all().order_by('-id')[:20]
    
    mempool = Mempool()
    latest_mempool_trx = mempool.get_mempool_transactions(quantity=20)
    #obtener los detalles del usuario, si es que está autenticado
    user_detail = None
    if request.user.is_authenticated:
        try:
            user_detail = request.user.userdetail
        except UserDetail.DoesNotExist:
            pass    
    #se retorna el template y a dicho template se le mandan las transacciones, el o los grupos
    #a los que pertence el usuario, las elecciones activas y los candidatos
    return render(request, 'home.html', {
        'latest_transactions_list' : latest_transactions_list,
        'user_in_group': user_in_group(request.user),
        'active_commissions': active_commissions,
        'candidate' : request.user, #acá si es un candidato, se debe enviar su información -> creo que esto sobra porque el request ya tiene los datos del usuario
        'user_detail' : user_detail,
        'latest_mempool_trx': latest_mempool_trx
    })

@login_required
# @permission_required('votations_app.can_view', raise_exception=True)
def start_voting_process(request):
    """el botón solo debe aparecer en el panel del admin y solo cuando no haya otra votación en proceso"""
    """Al presionar un botón, que se cree el bloqué génesis"""

    if request.method == 'GET':
        return render(request, 'start_commissions.html', {
            'user_in_group_and_has_permission': user_in_group_and_has_permission(request.user)
        })
    elif request.method == 'POST':
        user = User.objects.get(username=request.POST['creator'])
        if user is not None:
            try:
                #esta sección es para el tema de la fechas, incluyendo el try con aware y eso
                initial_date = request.POST['initial_date']
                final_date = request.POST['final_date']
                initial_hour = request.POST['initial_hour']
                final_hour = request.POST['final_hour']

                initial_datetime = initial_date + ' ' + initial_hour
                final_datetime = final_date + ' ' + final_hour

                try:
                    aware_initial_date = make_aware(datetime.strptime(initial_datetime, '%Y-%m-%d %H:%M'))
                    aware_final_date = make_aware(datetime.strptime(final_datetime, '%Y-%m-%d %H:%M'))
                except:
                    aware_initial_date = initial_datetime
                    aware_final_date = final_datetime
                #se crea la votación y se le asignan las fechas y eso
                votation = Votation.objects.create(creator=user,title=request.POST['title'],description=request.POST['description'],initial_date=aware_initial_date,final_date=aware_final_date)
                votation.save()

                #crear el bloque génesis desde acá
                blockchain = Blockchain(0)
                block = blockchain.create_genesis(votation=votation, user=user)
                print(block)
                
                messages.success(request, '¡Se ha creado un nuevo proceso electoral! El bloque génesis es ' + str(block.index))
                return redirect('home')
            except IntegrityError:
                return render(request, 'start_commissions.html', {
                    'error': 'Error: no se ha podido crear el proceso electoral.'
                })

@login_required
def vote_page(request, commission_id):
    #si llaman la página para la votación, se busca con el id cual es la votación solicitada (el id viene en la url)
    commission = get_object_or_404(Votation, pk=commission_id)
    #si se envia un get, es solo para mostrar la información
    if request.method == 'GET':
        #se retorna el template vote y se busca y envia a que grupo pertenece el usuario, 
        #los datos de la elección y los candidatos inscritos a dicha elección
        return render(request, 'vote.html', {
            'user_in_group': user_in_group(request.user),
            'commission' : commission,
            'candidates' : get_candidates(commission_id)
        })
    elif request.method == 'POST':
        #con la información enviada, se debe tomar el usuario, la votación y el voto a quien va
        commission_id = request.POST['commission_id']
        candidate_id = request.POST['candidate_id']

        # candidate_voted = UserProfile.objects.get(pk=candidate_id)
        
        print(commission_id, candidate_id)

        print(f'votante: {request.user.id} - name: {request.user.username}')

        user_actions = UserActions()
        #cuando el usuario vota, el usuario debe es encriptar sus datos y retornar la transacción encriptada y firmada
        vote_response = user_actions.voter_vote(request.user.id, candidate_id=candidate_id, commission_id=commission_id)
        print(vote_response)
        json_string = vote_response.content
        print(json_string)
        json_data = json.loads(json_string)
        print(json_data)
        status = json_data['status']
        message = json_data['message']
        print(f'status: {status}\n, message: {message}')
        
        if status == 'error' or isinstance(message, str):
            messages.error(request, message)
            return render(request, 'vote.html', {
                'user_in_group': user_in_group(request.user),
                'commission' : commission,
                'candidates' : get_candidates(commission_id)
            })
        
        vuser_id = message[1]
        cuser_id = message['cuser_id']
        enc_signature = message['enc_signature']
        enc_trx = message['enc_trx']
        print(f'status: {status}\n, message: {message}\n, vuser_id: {vuser_id}\n, cuser_id: {cuser_id}\n, enc_sig: {enc_signature}\n, enc_trx: {enc_trx}\n')
        if status != 'ok':
            messages.error(request, '¡Error, no se obtubo respuesta al realizar la votación!') 
        
        #se toma la firma y la transacción encriptada, se agrega a la mempool
        mempool = Mempool()
        mempool_trx = mempool.add_transaction(sender=vuser_id, sender_signature=enc_signature,
                                              recipient=cuser_id, trx_data=enc_trx,
                                              commission_id=commission_id)
        print('Transacción para la mempool:', mempool_trx)

        voter_checked = user_actions.user_has_voted_check(vote_response['vuser_id'])
        if voter_checked['status'] == 'ok':
            messages.error(request, '¡Error cambiando el estatus del votante!') 

        #pensamiento nocturno: no se deberia almacenar quien votó, se dice el milagro pero no el santo, solo se debería validar el usuario que vota
        #repensamiento: si se debe enviar quien vota para que se haga la validación de la transacción, el minero valida el usuario, los permisos
        #y que no haya votado antes, luego de esto agrega el voto si cumple a un bloque, y allí si descarta los datos del usuario :D

        #con esta información se debe agregar una transacción a la mempool
        # mempool = Mempool()
        # mempool_trx = mempool.add_transaction(commission_id=commission_id,sender=request.user, recipient=candidate_voted, vote=1)
        # print(mempool, mempool_trx)
        
        #1. Cada votante tiene una pareja de llaves pública-privada, y cada candidato también tiene una pareja de llaves pública-privada.
        #2. Cuando un votante desea emitir un voto, cifra su voto utilizando la llave pública del candidato. Además, genera un valor aleatorio, 
        # que se utilizará como prueba de que votó sin revelar por quién votó.
        
        #3. El votante envía su voto cifrado y el valor aleatorio a la red blockchain. Este paquete de datos también se firma digitalmente 
        # utilizando la llave privada del votante para asegurar la integridad del voto.
        #4. Cuando los mineros procesan la transacción, pueden verificar la firma digital utilizando la llave pública del votante. Esto confirma 
        # que el voto no ha sido alterado durante su transmisión y que proviene del votante correcto, sin revelar por quién votó.
        #5. Una vez confirmada la transacción, el voto cifrado se agrega a la blockchain. En este punto, el candidato puede descifrar el voto utilizando 
        # su llave privada.
        #6. Para contar los votos, los candidatos (o la entidad que administra la elección) descifran todos los votos válidos utilizando sus llaves 
        # privadas. Esto les permite contar los votos sin saber quién votó por quién.


        #cuando se vota, se debe cambiar el estado del votante a true, que si ha votado
        # user_detail = UserDetail.objects.get(pk=request.user.id)
        # user_detail.has_voted = True
        # user_detail.save()

        #luego de que en la mempool hayan suficientes transacciones, 
        #se le asigna a un nodo o el nodo la toma, y las agrega a un bloque
        #luego que se agrega y se valida el bloque, se agrega a la cadena
        
        messages.success(request, '¡Se ha realizado la votación!')
        
        #acá se retorna el comprobante del voto y se dehabilitan los botones para votar
        return render(request, 'vote.html', {
            'user_in_group': user_in_group(request.user),
            'commission' : commission,
            'candidates' : get_candidates(commission_id)
        })

@login_required
def add_node(request):
    # nodes_users = get_users_by_group('nodes')
    
    users = User.objects.filter(groups__name='nodes').exclude(node__isnull=False)
    users = users.values('id', 'username')
    users_list = list(users)

    register_nodes = Node.objects.filter(active=True)

    if request.method == 'GET':
        return render(request, 'add_node.html', {
            'user_in_group': user_in_group(request.user),
            'users': users_list,
            'register_nodes':register_nodes
        })
    elif request.method == 'POST':
        node_user = User.objects.get(id=request.POST['user_node'])
        ip_address = request.POST['ip_address'] #asignar una dirección ip x por ahora, usare la dirección web para las validaciones
        net_address = request.POST['net_address'] #la url del servidor nodo que se esta creando
        location = request.POST['location'] #ubicación física del nodo
        processing_capacity = request.POST['processing_capacity'] #capacidad de procesamiento del nodo
        
        node = Nodes()
        created_node = node.create_node(ip_address=ip_address, net_address=net_address, location=location
                                 ,processing_capacity=processing_capacity, user=node_user)

        messages.success(request, '¡Se ha agregado el nodo correctamente! El nodo se registró con el id: ' + created_node.node_id)
        return render(request, 'add_node.html', {
            'user_in_group': user_in_group(request.user),
            'users': users_list,
            'register_nodes':register_nodes
        })

@login_required
def update_node(request):
    #se toma la info del usuario que realiza la petición y se busca cual es el nodo creado por el admin
    #
    user = User.objects.get(pk=request.user.id)
    node = user.node

    if request.method == 'GET':
        return render(request, 'update_node.html', {
            'user_in_group': user_in_group(request.user),
            'node': node
        })
    elif request.method == 'POST':
        net_address = request.POST['net_address']
        location = request.POST['location'] 
        processing_capacity = request.POST['processing_capacity'] 
        password =  request.POST['password'] 
       
        node_method = Nodes()
        updated_node = node_method.update_node(user=user, node=node, net_address=net_address, location=location
                                        ,processing_capacity=processing_capacity, password=password)
        messages.success(request, '¡Se ha actualizado el nodo correctamente!')
        return redirect('home')

@login_required
def view_nodes(request):
    #retorna una view con una lista de los nodos registrados
    register_nodes = Node.objects.filter(active=True)
    return render(request, 'view_nodes.html', {
        'user_in_group': user_in_group(request.user),
        'register_nodes':register_nodes
    })

@login_required
def get_trxs(request):
    #si llaman la página para la votación, se busca con el id cual es la votación solicitada, sino, retorna error, solo para validación
    
    #si se envia un get, es solo para mostrar la información de lo que se esta minando -> en realidad ni debería entrar a este get.
    if request.method == 'GET':
        #se retorna el template vote y se busca y envia a que grupo pertenece el usuario, 
        #los datos de la elección y los candidatos inscritos a dicha elección
        # return render(request, 'mining.html', {
        #     'user_in_group': user_in_group(request.user)
        # })
        messages.info(request, '¡Se hizo un get desde no sé que página.!')
        return redirect('home')
    elif request.method == 'POST':
        commission_id = request.POST['commission_id']
        commission = get_object_or_404(Votation, pk=commission_id)
        print(f'elección: {commission}')
        #debe tomar las transacciones disponibles de la mempool que son de la votación seleccionada
        node = Node.objects.get(pk=request.user.id)
        #el minero crea un bloque temporal y a este bloque temporal es al que le agrega todas las transacciones
        #si ya se valida el bloque, ahí si se le pasa a la cadena real y se liga el bloque a la cadena de bloques
        #por temas de agilidad, se crea el bloque directamente en al cadena y allí se le agregan las transacciones

        # TODO ESTO LO DEBERÍA HACER EL MINERO, SE PONE ACÁ POR FACILIDAD. PERO ES UNA FUNCION LLAMADA "MINAR"
        mempool = Mempool()
        #nota: quitar la cantidad de acá para que queden por defecto
        print(f'related_vot: {commission_id}')
        mempool_trx = mempool.get_related_mem_trx(related_votation=commission_id,  quantity=2)
        print(mempool_trx)
        if not mempool_trx.exists():
            messages.info(request, '¡No hay transacciones que puedan ser minadas para la votación seleccionada!')
            return redirect('home')
        #una vez se han seleccionado las transacciones, se bloquean y se les asigna el nodo_id
        for memtrx in mempool_trx:
            mempool.update_status(memtrx.id, node.node_id)

        #crear el objeto blockchain con la información de la comision
        blockchain = Blockchain(commission_id)
        #obtener el último bloque de la cadena
        last_block = blockchain.get_last_block()
        print(f'bloque anterior: {last_block}')
        #hacer prueba de trabajo, se le envia el nonce del bloque anterior -> la prueba de trabajo deben ser las validaciones de autenticidad
        new_nonce = blockchain.proof_of_work(previous_nonce=last_block.nonce)
        print(f'nuevo nonce: {new_nonce}')
        #hashear las transacciones de la mempool (deberían ser las transacciones reales?) para agregarlas a la data
        data_hashed = blockchain.hash_data(mempool_trx)
        #crear el bloque, esto me retorna el bloque recien creado ->al crear el objeto se liga la cadena al objeto que se esta creando acá
        new_block = blockchain.create_block(nonce=new_nonce, previous_hash=last_block.previous_hash, data=data_hashed)
        print(f'nuevo bloque: {new_block}')
        #una vez creado el bloque, se le agregan las transacciones
        for trx in mempool_trx:
            trx_in_block = blockchain.add_transaction(sender=trx.sender, recipient=trx.recipient, vote=trx.vote, block=new_block)
            print(f'La transacción {trx.id} se agregó al bloque {trx_in_block} o -> {new_block.index}')
            mempool.delete_trx(trx_id=trx.id)
        
        #y como ya este nodo creo el bloque, se eliminan de la mempool
        #mempool.delete_trxs(related_votation=commission_id, node_id=node.node_id)

        #luego de que en la mempool hayan suficientes transacciones, 
        #se le asigna a un nodo o el nodo la toma, y las agrega a un bloque
        #luego que se agrega y se valida el bloque, se agrega a la cadena
        #luego el nodo debería validar la blockchain(?)

        messages.success(request, '¡Se ha minado correctamente el bloque!')
        return redirect('home')
        #acá se retorna el la notificación del minado correcto y se muestra lo que se ha minado
        # return render(request, 'home.html', {
        #     'user_in_group': user_in_group(request.user),
        #     'commission' : commission,
        #     'new_block' : new_block
        # })

def user_in_group_and_has_permission(user):
    # if user.groups.filter(name="grupo_especifico").exists() and user.has_perm('app_name.permiso_necesario'):
    if user.groups.filter(name="admins").exists():
        return True
    return False

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

def get_users_by_group(group_name):
    users = User.objects.filter(groups__name=group_name).values('id', 'username')
    return list(users)

def active_commissions():
    return Votation.get_active_votations()

def get_candidates(commission_id):
    """
    los candidatos se obtienen con base a los grupos asociados y si en la lista de UserDetail es candidato o es sustituto
    además, se debe validar que se busquen los usuarios que esten ligados unicamente a la votación actual
    """
    # candidates = Group.objects.get(name='candidates')
    # return candidates.user_set.all()

    #obtener la votación actual
    votations = Votation.objects.get(pk=commission_id) 
    #obtener los candidatos de los grupos -para validar que si esten en el grupo correcto
    candidates = Group.objects.get(name='candidates').user_set.all()
    #obtener de la votación actual, los usuarios específicos --para validar que si estén asociados a las elecciones actuales
    votations_candidates = votations.users.filter(id__in=candidates)
    #obtener los detalles de los candidatos registrados en la votación actual --para verificar que tipo de candidatos son (candidato o suplente) y sus agrupaciones
    #candidates_details = UserDetail.objects.filter(user__in=votations_candidates)

    #ahora resta hacer las validaciones, se debe mandar en grupo los candidatos y sus respectivos grupos
    #print(votations_candidates, candidates_details)
    #candict = dict(zip(votations_candidates, candidates_details))
    return votations_candidates.order_by('-userdetail__is_candidate', 'userdetail__candidate_group')



from django.http import HttpResponseBadRequest


"""
En este ejemplo, estamos obteniendo la instancia del usuario actual (request.user) y la instancia de Votation correspondiente al 
votacion_id proporcionado. Luego, estamos obteniendo la instancia de UserVotation correspondiente al usuario y la votación en cuestión, 
y verificando que el usuario sea un candidato en la votación mediante el campo is_candidate. Si el usuario es un candidato, estamos 
obteniendo las propuestas del formulario (request.POST.get('propuestas')) y guardándolas en el campo proposals de la instancia de 
UserVotation. Finalmente, estamos redirigiendo al usuario a la página de detalles de la votación.
"""
# def guardar_propuestas(request, votacion_id):
#     if request.method == 'POST':
#         user = request.user
#         votacion = Votation.objects.get(id=votacion_id)
#         try:
#             user_votation = UserVotation.objects.get(user=user, votation=votacion)
#         except UserVotation.DoesNotExist:
#             return HttpResponseBadRequest("El usuario no está asociado a esta votación")
#         if not user_votation.is_candidate:
#             return HttpResponseBadRequest("El usuario no es candidato en esta votación")

#         propuestas = request.POST.get('propuestas')
#         user_votation.proposals = propuestas
#         user_votation.save()
#         return redirect('votacion_detalle', votacion_id=votacion_id)
#     else:
#         return render(request, 'formulario_propuestas.html')
