from django.urls import path
from .views import (
    RegistroView, LoginView, PerfilView,
    VerifyTokenView, change_password, LogoutView, health_check
)

urlpatterns = [
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
    path('verify/', VerifyTokenView.as_view(), name='token-verify'),
    path('change-password/', change_password, name='change_password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("health/", health_check, name="health-check"),
]