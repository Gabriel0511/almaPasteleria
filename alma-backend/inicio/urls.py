from django.urls import path
from .views import (
    RegistroView, LoginView, PerfilView,
    VerifyTokenView, change_password, LogoutView,
    PasswordResetRequestView, VerifyResetCodeView, ResetPasswordView
)

urlpatterns = [
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
    path('verify/', VerifyTokenView.as_view(), name='token-verify'),
    path('change-password/', change_password, name='change_password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # Recuperación de contraseña
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('verify-reset-code/', VerifyResetCodeView.as_view(), name='verify-reset-code'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]