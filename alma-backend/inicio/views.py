from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import UsuarioSerializer, LoginSerializer

import random, webbrowser
from django.contrib.auth.hashers import make_password
User = get_user_model()

# ================================
# 🔹 Reset de contraseña por WhatsApp
# ================================
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')  # Formato: 5491123456789 (sin +)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Email no registrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generar código
        reset_code = str(random.randint(100000, 999999))
        cache.set(f'reset_{email}', reset_code, timeout=900)

        # ✅ SOLUCIÓN: Solo devolver la URL, NO abrir WhatsApp
        whatsapp_url = f"https://wa.me/{phone}?text=Tu%20código%20es:%20{reset_code}"
        
        
        # ✅ En desarrollo, puedes loguear la URL
        print(f"[DEV] WhatsApp URL: {whatsapp_url}")
        
        return Response({
            'detail': 'Código generado. Abre WhatsApp manualmente.',
            'whatsapp_url': whatsapp_url,  # ✅ Devuelve la URL
            'code': reset_code  # ✅ Solo para desarrollo, quitar en producción
        }, status=200)

class VerifyResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        cached_code = cache.get(f'reset_{email}')
        
        if not cached_code or cached_code != code:
            return Response(
                {'error': 'Código inválido o expirado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generar token temporal (válido solo para reset)
        user = User.objects.get(email=email)
        token = RefreshToken.for_user(user).access_token
        cache.set(f'reset_token_{email}', str(token), timeout=3600)  # 1 hora
        
        return Response({
            'detail': 'Código verificado',
            'email': email  # Para el siguiente paso
        }, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        
        # Verificar que el email existe
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar la contraseña
        user.password = make_password(new_password)
        user.save()
        
        # Limpiar cualquier token/código en caché
        cache.delete(f'reset_token_{email}')
        
        return Response(
            {'detail': 'Contraseña actualizada correctamente'},
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
