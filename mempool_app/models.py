from django.db import models
from django.contrib.auth.models import User

   
class MempoolTransaction(models.Model):
    # Campos de la tabla de transacciones (ya minados, es decir, que ya pasaron por la mempool)
    sender = models.CharField(max_length=100) #quien envia la transacción, se envia el user_id para que el nodo pueda validar la firma
    sender_signature = models.CharField(max_length=500) #la firma es un hash encriptado con la llave privada del votante y que se descifra con la llave pública
    trx_data = models.CharField(max_length=500) #acá se almacena la información encriptada que se envia en la transacción al candidato
    timestamp = models.DateTimeField(auto_now_add=True) #desde el momento en que se crea
    is_taken = models.BooleanField(default=False) #se marca cuando un nodo toma la transacción
    related_votation = models.PositiveIntegerField(default=1) #Solo se envía el id de la votación para que la mempool haga sus validaciones y no se caiga por una relación
    node_id = models.CharField(max_length=100) #nodo que toma la transacción
    # sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_mempool')  #16/05/2023 se eliminan estos campos porque se requiere mas transparencia en la votación
    # recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient_mempool') #16/05/2023
    #node_id = models.CharField(max_length=100, default='nodeidtodelete12345678') #16/05/2023 borro el default porque aja, ya se supone no se requiere

# se debe definir que un minero tome la transaccion (un minero es un tipo de nodo que toma transacciones y las valida y crea el bloque)
# y el nodo acá sera quien tome los bloques del minero y los agregue a la base de datos    
    
    def __str__(self):
        return f"{self.sender} envia transacción la mempool."
    