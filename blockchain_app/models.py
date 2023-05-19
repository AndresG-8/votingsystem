from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone
from votations_app.models import Votation

import hashlib
# Modelos ORM de base de datos de la Blockchain

class Chain(models.Model):
    votation = models.ForeignKey(Votation, on_delete=models.CASCADE, related_name='chain', default=1)
    timestamp = models.DateTimeField(auto_now_add=True) # Fecha y hora en la que se creó el bloque
    
    def __str__(self):
        return f"Cadena {self.id} de la votación {self.votation.title}"

class Block(models.Model):
    # Campos de la tabla de bloques
    index = models.IntegerField() # Índice del bloque en la cadena
    timestamp = models.DateTimeField(auto_now_add=True) # Fecha y hora en la que se creó el bloque
    data = models.TextField() # Datos almacenados en el bloque-datos x, por ejemplo, quien lo minó y así
    previous_hash = models.CharField(max_length=64) # Hash del bloque anterior
    nonce = models.IntegerField() # Número utilizado en la prueba de trabajo para generar el hash del bloque
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return f"Block {self.id} con index {self.index}"

class Transaction(models.Model):
    # Campos de la tabla de transacciones (ya minados, es decir, que ya pasaron por la mempool)
    sender = models.CharField(max_length=100) #quien envia la transacción, se envia el user_id para que el nodo pueda validar la firma
    sender_signature = models.CharField(max_length=500, default='0') #la firma es un hash encriptado con la llave privada del votante y que se descifra con la llave pública
    trx_data = models.CharField(max_length=500, default='0') #acá se almacena la información encriptada que se envia en la transacción al candidato
    timestamp = models.DateTimeField(auto_now_add=True)
    node_id = models.CharField(max_length=100, default='0') #nodo que agrega la transacción
    block = models.ForeignKey(Block, on_delete=models.CASCADE,default=0)

    def __str__(self):
        return f"se emite voto de {self.sender} y se agrega con id: {self.id} el {self.timestamp}."


    
