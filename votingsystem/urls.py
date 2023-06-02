"""
URL configuration for votingsystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls, name = 'admin'), #front
    path('blockchain/', include('blockchain_app.urls')), #estilo api, no front
    path('', include('votations_app.urls')), #front y back - 
    path('users/', include('users_app.urls')), #front y back - tiene la lógica para el registro, ingreso y salida de la app
    path('miners/', include('miners_app.urls')), #estilo api, no front -por ahora está vacío
    path('nodes/', include('nodes_app.urls')), #estilo api, no front -por ahora está vacío
    path('mempool/', include('mempool_app.urls')), #estilo api, no front -por ahora está vacío
]
