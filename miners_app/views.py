from django.shortcuts import render
from django.http import HttpResponse

from mempool_app.models import MempoolTransaction
def index(request):
    return HttpResponse('Hola mundo con miners')

class Miners():
    """
    Esta aplicación se encarga de tomar las transacciones y agregarlas a la Blockchain
    para esto es necesario saber cuales son los nodos, las transacciones que hay en la mempool
    armar el bloque, minarlo y enviarlo.
    """
    def __init__(self) -> None:
        # self.commission = 
        pass

    """
    Un minero(nodo) registrado obtiene las transacciones de la mempool
    Se crea el objeto de la Blockchain, esto debe saber a que cadena esta agregando las transacciones
    se obtiene el bloque (para extraer la información y ponerla en el bloque actual)
    
    Se hace la prueba de trabajo

    Se crea el bloque actual --como hacer para crearlo sin enviarlo a la blockchain? esto solo se debería agregar en caso de ser validado
    Se crean las transacciones con base en la información obtenida de la mempool (acá se limpian los datos privados de usuario o se hashean)
    Se agregan las transacciones al bloque
    Se crea el listado con las transacciones del bloque
    Se hashea el listado con las transacciones para agregarlo al campo data
    
    """
    def get_mempool_trx():
        mempool = MempoolTransaction()
        mempool_trx_list = mempool.get_mempool_transactions()
        return mempool_trx_list
    
    # def get_chain():
    #     """
    #     Solo ha de tomar las transacciones de una cadena específica... 
    #     pero cual y como"""
    #     get_related_mem_trx
    def mine():
        pass
    
