from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import UsuarioSerializer, LoginSerializer

import random, string, hashlib, time
from django.contrib.auth.hashers import make_password
User = get_user_model()

# ================================
# 🔹 Reset de contraseña por WhatsApp
# ================================
# ================================
# 🔹 Helper Functions
# ================================
def generate_secure_code():
    """Genera un código seguro de 8 caracteres"""
    # 6 dígitos + 2 letras para mayor seguridad
    digits = ''.join(random.choices(string.digits, k=6))
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    code = digits + letters
    # Mezclar
    code_list = list(code)
    random.shuffle(code_list)
    return ''.join(code_list)

def send_reset_email(email, reset_code):
    """Envía el email con el código de recuperación"""
    try:
        context = {
            'reset_code': reset_code,
            'year': timezone.now().year,
        }
        
        # Renderizar templates
        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = render_to_string('emails/password_reset.txt', context)
        
        # Enviar email
        send_mail(
            subject='🔐 Restablecer Contraseña - Alma Pastelería',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error enviando email: {str(e)}")
        return False

# ================================
# 🔹 Recuperación por Email
# ================================
class PasswordResetRequestView(APIView):
    """
    Solicitar restablecimiento de contraseña por email
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        
        if not email:
            return Response(
                {'error': 'El email es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el email existe (pero no revelar si no existe por seguridad)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Por seguridad, siempre devolvemos éxito aunque el email no exista
            return Response({
                'detail': 'Si el email existe en nuestro sistema, recibirás un código de recuperación.'
            }, status=status.HTTP_200_OK)
        
        # Verificar si ya hay un código activo (rate limiting)
        last_request = cache.get(f'reset_cooldown_{email}')
        if last_request:
            remaining = 60 - (time.time() - last_request)
            if remaining > 0:
                return Response({
                    'error': f'Espera {int(remaining)} segundos antes de solicitar otro código'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Generar código seguro
        reset_code = generate_secure_code()
        
        # Guardar en caché con timestamp y metadata
        cache_data = {
            'code': reset_code,
            'email': email,
            'created_at': time.time(),
            'attempts': 0,  # Contador de intentos fallidos
            'verified': False
        }
        
        # Guardar código por 15 minutos (900 segundos)
        cache.set(f'password_reset_{email}', cache_data, timeout=900)
        
        # Guardar timestamp para rate limiting (60 segundos)
        cache.set(f'reset_cooldown_{email}', time.time(), timeout=60)
        
        # Enviar email
        email_sent = send_reset_email(email, reset_code)
        
        if not email_sent:
            return Response({
                'error': 'Error al enviar el email de recuperación'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Registrar en logs (solo en desarrollo)
        if settings.DEBUG:
            print(f"[DEV] Código de recuperación para {email}: {reset_code}")
        
        return Response({
            'detail': 'Código de recuperación enviado por email',
            'email': email,
            'expires_in': 900,  # segundos
            'cooldown': 60  # segundos para próximo envío
        }, status=status.HTTP_200_OK)


class VerifyResetCodeView(APIView):
    """
    Verificar el código de recuperación
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        code = request.data.get('code', '').strip().upper()
        
        if not email or not code:
            return Response(
                {'error': 'Email y código son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener datos de caché
        cache_data = cache.get(f'password_reset_{email}')
        
        if not cache_data:
            return Response(
                {'error': 'Código expirado o no solicitado. Solicita un nuevo código.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Incrementar contador de intentos
        cache_data['attempts'] += 1
        
        # Verificar intentos máximos (3 intentos)
        if cache_data['attempts'] > 3:
            cache.delete(f'password_reset_{email}')
            return Response(
                {'error': 'Demasiados intentos fallidos. Solicita un nuevo código.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar código
        if cache_data['code'] != code:
            # Guardar intento fallido
            cache.set(f'password_reset_{email}', cache_data, timeout=900)
            remaining_attempts = 3 - cache_data['attempts']
            
            return Response({
                'error': f'Código incorrecto. Te quedan {remaining_attempts} intentos.',
                'attempts': cache_data['attempts'],
                'remaining_attempts': remaining_attempts
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Marcar como verificado
        cache_data['verified'] = True
        cache_data['verified_at'] = time.time()
        cache.set(f'password_reset_{email}', cache_data, timeout=600)  # 10 minutos para cambiar contraseña
        
        # Generar token único para cambio de contraseña
        verification_token = hashlib.sha256(f"{email}{code}{time.time()}".encode()).hexdigest()[:32]
        cache.set(f'reset_token_{verification_token}', email, timeout=600)
        
        return Response({
            'detail': 'Código verificado correctamente',
            'email': email,
            'token': verification_token,  # Token para el siguiente paso
            'expires_in': 600  # 10 minutos para cambiar contraseña
        }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    Cambiar la contraseña después de verificación
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        # Validaciones básicas
        if not email or not new_password:
            return Response(
                {'error': 'Email y nueva contraseña son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar token (si se proporciona)
        if token:
            cached_email = cache.get(f'reset_token_{token}')
            if not cached_email or cached_email != email:
                return Response(
                    {'error': 'Token inválido o expirado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Verificación alternativa con código en caché
            cache_data = cache.get(f'password_reset_{email}')
            if not cache_data or not cache_data.get('verified'):
                return Response(
                    {'error': 'Debes verificar el código primero'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validar fortaleza de contraseña
        if len(new_password) < 8:
            return Response(
                {'error': 'La contraseña debe tener al menos 8 caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el usuario existe
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
        
        # Limpiar caché
        cache.delete(f'password_reset_{email}')
        if token:
            cache.delete(f'reset_token_{token}')
        cache.delete(f'reset_cooldown_{email}')
        
        # Enviar email de confirmación
        try:
            send_mail(
                subject='✅ Contraseña Actualizada - Alma Pastelería',
                message=f'Hola,\n\nTu contraseña en Alma Pastelería ha sido actualizada exitosamente.\n\nSi no realizaste este cambio, contacta a soporte inmediatamente.\n\nSaludos,\nEquipo Alma Pastelería',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
        except:
            pass  # No crítico si falla el email de confirmación
        
        return Response(
            {'detail': 'Contraseña actualizada correctamente. Ya puedes iniciar sesión.'},
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
