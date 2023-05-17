from django.urls import path, include
from .views import index

urlpatterns = [
    path('', index, name = 'index'),
    path('transactions/', include('votations_app.urls')),
]