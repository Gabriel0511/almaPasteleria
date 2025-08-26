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
                for detalle in detalles:
                    cantidad_necesaria = detalle.get_cantidad_en_unidad_insumo()
                    
                    if detalle.insumo.stock_actual < cantidad_necesaria:
                        return Response(
                            {'error': f'Stock insuficiente de {detalle.insumo.nombre}. Necesitas {cantidad_necesaria} {detalle.insumo.unidad_medida.abreviatura}, tienes {detalle.insumo.stock_actual}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                # Reducir stock
                for detalle in detalles:
                    cantidad_necesaria = detalle.get_cantidad_en_unidad_insumo()
                    detalle.insumo.stock_actual -= cantidad_necesaria
                    detalle.insumo.save()
                
                receta.veces_hecha += 1
                receta.save()
                
                return Response({
                    'nuevo_contador': receta.veces_hecha,
                    'stock_actualizado': True
                }, status=status.HTTP_200_OK)
                
        except Receta.DoesNotExist:
            return Response(
                {'error': 'Receta no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

class DecrementarRecetaView(APIView):
    def post(self, request, pk):
        try:
            with transaction.atomic():
                receta = Receta.objects.get(pk=pk)
                if receta.veces_hecha <= 0:
                    return Response(
                        {'error': 'El contador ya está en cero'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                detalles = RecetaInsumo.objects.filter(receta=receta)
                
                # Devolver insumos al stock
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
                
                receta.veces_hecha -= 1
                receta.save()
                
                return Response({
                    'nuevo_contador': receta.veces_hecha,
                    'stock_actualizado': True
                }, status=status.HTTP_200_OK)
                
        except Receta.DoesNotExist:
            return Response(
                {'error': 'Receta no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )