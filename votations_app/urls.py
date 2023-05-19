from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('start-commissions/', views.start_voting_process, name='start_commissions'),
    path('add_node/', views.add_node, name='add_node'),
    path('update_node/', views.update_node, name='update_node'),
    path('view_nodes/', views.view_nodes, name='view_nodes'),
    path('vote/<int:commission_id>/', views.vote_page, name='vote'),
    path('get_trxs/', views.get_trxs, name='get_trxs'),
    path('count_votes/', views.count_votes, name='count_votes'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)