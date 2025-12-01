from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.core.cache import cache
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import UsuarioSerializer, LoginSerializer
import resend
import random
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

# Configurar Resend
resend.api_key = settings.RESEND_API_KEY

def send_reset_email(email, reset_code):
    """Enviar email usando Resend API"""
    try:
        # Crear contenido HTML y texto plano
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Código de recuperación</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #8d6e69;">🔐 Recuperación de Contraseña</h2>
                <p>Hola,</p>
                <p>Has solicitado restablecer tu contraseña en <strong>Alma Pastelería</strong>.</p>
                <div style="background-color: #f4f4f4; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
                    <p style="font-size: 14px; color: #666;">Tu código de verificación es:</p>
                    <h1 style="font-size: 32px; letter-spacing: 5px; color: #8d6e69; margin: 10px 0;">{reset_code}</h1>
                    <p style="font-size: 12px; color: #999;">Este código expira en 15 minutos</p>
                </div>
                <p>Si no solicitaste este cambio, por favor ignora este mensaje.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #999;">© {timezone.now().year} Alma Pastelería. Todos los derechos reservados.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Recuperación de Contraseña - Alma Pastelería
        
        Tu código de verificación es: {reset_code}
        
        Este código expira en 15 minutos.
        
        Si no solicitaste este cambio, por favor ignora este mensaje.
        
        © {timezone.now().year} Alma Pastelería
        """

        # Enviar email con Resend
        params = {
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": email,
            "subject": "🔐 Código de Recuperación - Alma Pastelería",
            "html": html_content,
            "text": text_content,
        }

        email_response = resend.Emails.send(params)
        logger.info(f"Email enviado a {email}: {email_response}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando email con Resend: {str(e)}")
        return False

# ================================
# 🔹 Reset de contraseña por EMAIL
# ================================
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Por seguridad, no revelamos si el email existe o no
            return Response(
                {'detail': 'Si el email está registrado, recibirás un código de recuperación.'},
                status=status.HTTP_200_OK
            )

        # Generar código de 6 dígitos
        reset_code = str(random.randint(100000, 999999))
        
        # Guardar en cache con email como clave
        cache_key = f'password_reset_{email}'
        cache_data = {
            'code': reset_code,
            'attempts': 3,  # 3 intentos máximo
            'verified': False
        }
        cache.set(cache_key, cache_data, timeout=900)  # 15 minutos

        # Enviar email usando Resend
        email_sent = send_reset_email(email, reset_code)
        
        if not email_sent:
            return Response(
                {'error': 'Error al enviar el email. Por favor intenta más tarde.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'detail': 'Código enviado. Revisa tu email (y spam).',
            'email': email
        }, status=status.HTTP_200_OK)


class VerifyResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response(
                {'error': 'Email y código son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cache_key = f'password_reset_{email}'
        cached_data = cache.get(cache_key)
        
        if not cached_data:
            return Response(
                {'error': 'Código expirado o no solicitado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar intentos
        if cached_data['attempts'] <= 0:
            cache.delete(cache_key)
            return Response(
                {'error': 'Demasiados intentos fallidos. Solicita un nuevo código.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar código
        if cached_data['code'] != code:
            cached_data['attempts'] -= 1
            cache.set(cache_key, cached_data, timeout=900)
            
            return Response({
                'error': 'Código incorrecto',
                'remaining_attempts': cached_data['attempts']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Código correcto
        cached_data['verified'] = True
        cache.set(cache_key, cached_data, timeout=600)  # 10 minutos para cambiar contraseña
        
        # Generar token JWT temporal
        user = User.objects.get(email=email)
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'detail': 'Código verificado correctamente',
            'email': email,
            'token': str(refresh.access_token)  # Token temporal para reset
        }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        token = request.data.get('token')
        
        # Verificar que todos los campos están presentes
        if not email or not new_password:
            return Response(
                {'error': 'Email y nueva contraseña son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar longitud mínima de contraseña
        if len(new_password) < 8:
            return Response(
                {'error': 'La contraseña debe tener al menos 8 caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar cache para email verificado
        cache_key = f'password_reset_{email}'
        cached_data = cache.get(cache_key)
        
        if not cached_data or not cached_data.get('verified'):
            return Response(
                {'error': 'Verificación requerida. Solicita un nuevo código.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar la contraseña
        user.set_password(new_password)
        user.save()
        
        # Limpiar cache
        cache.delete(cache_key)
        
        # Invalidar tokens existentes (opcional, mejora seguridad)
        from rest_framework_simplejwt.tokens import RefreshToken
        RefreshToken.for_user(user)
        
        return Response(
            {'detail': 'Contraseña actualizada exitosamente'},
            status=status.HTTP_200_OK
        )



# ================================
# 🔹 Autenticación
# ================================
class RegistroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UsuarioSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Sesión cerrada exitosamente"}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VerifyTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"detail": "Token válido"})


# ================================
# 🔹 Perfil y cambio de contraseña
# ================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    form = PasswordChangeForm(request.user, request.data)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return Response({"detail": "Contraseña actualizada exitosamente"}, status=status.HTTP_200_OK)

    errors = {
        'old_password': form.errors.get('old_password'),
        'new_password1': form.errors.get('new_password1'),
        'new_password2': form.errors.get('new_password2'),
    }
    return Response({
        'detail': 'Error al cambiar la contraseña',
        'errors': {k: v for k, v in errors.items() if v}
    }, status=status.HTTP_400_BAD_REQUEST)


class PerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)
