from django.urls import path, include
from . import views
# from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signin', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('signout', views.signout, name='signout'),
    path('profile', views.profile, name='profile'),
    # path("accounts/", include("django.contrib.auth.urls")),
    # path("change-password/", auth_views.PasswordChangeView.as_view()),
]