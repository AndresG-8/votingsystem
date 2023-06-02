from django.shortcuts import render
from django.http import HttpResponse
from .models import MempoolTransaction

def index(request):
    return HttpResponse('Hola mundo con mempool')

#esta clase recibe las transacciones, cada que entra una transacción se agrega a la lista o bd de transacciones
#estas transacciones se han de mandar a los nodos mineros para que la procesen, o dejar que los nodos la tomen
#pero al enviar una transaccion para que un nodo la tome, se debería bloquear? 

#como es una blockchain privada, podría ser que cada 10 transacciones agregadas, se busque en los nodos mineros cual
#esta disponible, y el primero que se vea que no haya minado hace poco, se le envian las 10 transacciones, así
#el nodo minero genera el bloque, al generar el bloque, la transaccion se envia a la BLockchain
class Mempool:
    """Clase mempool, la cual gestiona las transacciones temporales que se han de redistribuir entre los nodos disponibles"""
    
    def __init__(self):
        """al llamar la clase, se debe verificar la cantidad de transacciones en la base de datos que no esten tomadas por un minero
        se debe correr algo para que cada cierto tiempo se verifique si la transacción lleva x tiempo en la cola, si lleva mucho
        se debe quitar el bloqueo para que se asigne a otro minero, si se quita el bloqueo de una trx se debe cancelar el bloque
        que el minero al que se le quito la transacción tiene"""
        
    @staticmethod
    def add_transaction(sender, sender_signature, trx_data, commission_id):
        """
        Agrega una transacción a la mempool, retorna la transacción en sí
        """
        transaction = MempoolTransaction.objects.create(sender=sender, sender_signature=sender_signature, trx_data=trx_data, related_votation=commission_id)
        transaction.save()
        return transaction
    
    @staticmethod
    def get_mempool_transactions(quantity=None, taken=False):
        """
        Obtiene transacciones y las retorna en el queryset
        """
        if quantity != None:
            return MempoolTransaction.objects.filter(is_taken=taken).order_by('-id')[:quantity]
        else:
            return MempoolTransaction.objects.filter(is_taken=taken).order_by('-id')
    
    @staticmethod
    def get_related_mem_trx(related_votation, quantity=10, taken=False):
        """Se retornan todas las transacciones de una votación específica y por defecto solo 10 transacciones que no esten tomadas ya"""
        return MempoolTransaction.objects.filter(is_taken=taken, related_votation=related_votation).order_by('id')[:quantity]

    @staticmethod
    def get_taken_trx(related_votation, node_id, quantity=10):
        """Recibe el id del nodo y retorna las transacciones que dicho nodo tiene tomadas"""
        return MempoolTransaction.objects.filter(is_taken=True, related_votation=related_votation, node_id=node_id).order_by('id')[:quantity]

    @staticmethod
    def update_status(mem_trx_id, node_id):
        mempool_trx = MempoolTransaction.objects.get(id=mem_trx_id)
        mempool_trx.node_id = node_id
        mempool_trx.is_taken = True
        mempool_trx.save()
        return True
    
    @staticmethod
    def delete_trxs(related_votation, node_id):
        MempoolTransaction.objects.filter(is_taken=True, related_votation=related_votation, node_id=node_id).delete()

    @staticmethod
    def delete_trx(trx_id):
        MempoolTransaction.objects.get(id=trx_id).delete()

