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
        return f"Block {self.index}"

class Transaction(models.Model):
    # Campos de la tabla de transacciones (ya minados, es decir, que ya pasaron por la mempool)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions')
    vote = models.PositiveSmallIntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)
    block = models.ForeignKey(Block, on_delete=models.CASCADE,default=0)
    
    def __str__(self):
        return f"{self.recipient} ha recibido {self.vote} votó el {self.timestamp} ->eliminar esto: {self.sender}"


    
