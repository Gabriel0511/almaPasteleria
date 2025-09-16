from rest_framework import generics, permissions
from .models import Receta, RecetaInsumo
from .serializers import RecetaSerializer, RecetaInsumoSerializer
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from pedidos.models import Pedido
from insumos.models import Insumo
from insumos.conversiones import convertir_unidad

class RecetaListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Receta.objects.all().order_by('-creado_en')
    serializer_class = RecetaSerializer

    def perform_create(self, serializer):
        # Log para debugging
        print("Datos recibidos:", self.request.data)
        serializer.save()

class RecetaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Receta.objects.all()
    serializer_class = RecetaSerializer
    permission_classes = [permissions.IsAuthenticated]

class RecetaInsumoListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RecetaInsumoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        receta_id = self.kwargs['receta_id']
        return RecetaInsumo.objects.filter(receta_id=receta_id)

    def perform_create(self, serializer):
        receta_id = self.kwargs['receta_id']
        serializer.save(receta_id=receta_id)

class RecetaInsumoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecetaInsumoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        receta_id = self.kwargs['receta_id']
        return RecetaInsumo.objects.filter(receta_id=receta_id)
    
class IncrementarRecetaView(APIView):
    def post(self, request, pk):
        try:
            with transaction.atomic():
                receta = Receta.objects.get(pk=pk)
                detalles = RecetaInsumo.objects.filter(receta=receta)
                
                # Verificar stock antes de incrementar
                insuficientes = []
                for detalle in detalles:
                    cantidad_necesaria = detalle.get_cantidad_en_unidad_insumo()
                    
                    if detalle.insumo.stock_actual < cantidad_necesaria:
                        insuficientes.append({
                            'nombre': detalle.insumo.nombre,
                            'disponible': float(detalle.insumo.stock_actual),
                            'necesario': float(cantidad_necesaria),
                            'unidad': detalle.insumo.unidad_medida.abreviatura
                        })
                
                if insuficientes:
                    return Response({
                        'error': 'Stock insuficiente para preparar la receta',
                        'insuficientes': insuficientes,
                        'receta_nombre': receta.nombre
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Reducir stock
                for detalle in detalles:
                    cantidad_necesaria = detalle.get_cantidad_en_unidad_insumo()
                    detalle.insumo.stock_actual -= cantidad_necesaria
                    detalle.insumo.save()
                
                receta.veces_hecha += 1
                receta.save()
                
                return Response({
                    'nuevo_contador': receta.veces_hecha,
                    'stock_actualizado': True,
                    'mensaje': f'Receta "{receta.nombre}" preparada exitosamente'
                }, status=status.HTTP_200_OK)
                
        except Receta.DoesNotExist:
            return Response({
                'error': 'Receta no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error interno del servidor: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DecrementarRecetaView(APIView):
    def post(self, request, pk):
        try:
            with transaction.atomic():
                receta = Receta.objects.get(pk=pk)
                if receta.veces_hecha <= 0:
                    return Response({
                        'error': 'El contador ya está en cero',
                        'receta_nombre': receta.nombre
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                detalles = RecetaInsumo.objects.filter(receta=receta)
                
                # Devolver insumos al stock
                insumos_devueltos = []
                for detalle in detalles:
                    insumo = detalle.insumo
                    cantidad_devolver = detalle.cantidad
                    
                    # Convertir a la unidad de medida del insumo
                    if detalle.unidad_medida != insumo.unidad_medida:
                        cantidad_devolver = convertir_unidad(
                            detalle.cantidad,
                            detalle.unidad_medida.abreviatura,
                            insumo.unidad_medida.abreviatura
                        )
                    
                    insumo.stock_actual += cantidad_devolver
                    insumo.save()
                    
                    insumos_devueltos.append({
                        'nombre': insumo.nombre,
                        'cantidad': float(cantidad_devolver),
                        'unidad': insumo.unidad_medida.abreviatura
                    })
                
                receta.veces_hecha -= 1
                receta.save()
                
                return Response({
                    'nuevo_contador': receta.veces_hecha,
                    'stock_actualizado': True,
                    'mensaje': f'Se ha revertido la preparación de "{receta.nombre}"',
                    'insumos_devueltos': insumos_devueltos
                }, status=status.HTTP_200_OK)
                
        except Receta.DoesNotExist:
            return Response({
                'error': 'Receta no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error interno del servidor: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)