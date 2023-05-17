from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Node(models.Model):
    node_id = models.CharField(max_length=100, unique=True) #identificador único del nodo, lo podría sacar con el uuid4
    ip_address = models.CharField(max_length=50) #la dirección IP del nodo
    net_address = models.CharField(max_length=250) # la dirección web del nodo, cada nodo será un servidor, por lo que debe tener capacidad de ello
    public_key = models.CharField(max_length=500) # llave pública que puede ser consultada por cualquiera, se hace con la clave del usuario nodo y el node_id
    private_key = models.CharField(max_length=500) # podría recrearse solo en tiempo de ejecución, cuando el nodo esté funcionando, se hace con la clave del usuario nodo y el node_id
    location = models.CharField(max_length=100, null=True, blank=True) # ubicación del nodo, geográficamente
    processing_capacity = models.IntegerField(null=True, blank=True) # capacidad de procesamiento del nodo determinado por la cantidad de transacciones que puede procesar en x periodo
    active = models.BooleanField(default=True) #para determinar cuando un usuario nodo está activo y ejecutando los nodos
    user = models.OneToOneField(User, on_delete=models.CASCADE) # se relaciona con el usuario para que se recree la llave privada en tiempo de ejecución

    def __str__(self):
        return self.node_id
