from django.urls import path
from .views import RegistroView, LoginView, PerfilView, VerifyTokenView

urlpatterns = [
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
    path('verify/', VerifyTokenView.as_view(), name='token-verify'),
]