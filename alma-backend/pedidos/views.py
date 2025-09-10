# views.py - Versión corregida
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.utils import timezone
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from .models import Pedido, DetallePedido, Cliente, IngredientesExtra
from .serializers import IngredientesExtraWriteSerializer, PedidoWriteSerializer, PedidoReadSerializer, DetallePedidoWriteSerializer, DetallePedidoReadSerializer, ClienteSerializer
from recetas.models import Receta
from insumos.models import Insumo

class PedidosHoyView(APIView):
    def get(self, request):
        hoy = date.today()
        
        entregar_hoy = Pedido.objects.filter(
            fecha_entrega=hoy,
            estado__in=['pendiente', 'en preparación']
        )
        
        hacer_hoy = Pedido.objects.filter(
            fecha_fabricacion=hoy,
            estado__in=['pendiente', 'en preparación']
        )
        
        entregar_serializer = PedidoReadSerializer(entregar_hoy, many=True)  # ← Cambiado
        hacer_serializer = PedidoReadSerializer(hacer_hoy, many=True)  # ← Cambiado
        
        return Response({
            'entregar_hoy': entregar_serializer.data,
            'hacer_hoy': hacer_serializer.data
        }, status=status.HTTP_200_OK)

class ActualizarEstadoPedidoView(APIView):
    def patch(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        nuevo_estado = request.data.get('estado')
        
        # Validar transición de estado
        if pedido.estado in ['pendiente', 'en preparación'] and nuevo_estado == 'entregado':
            pedido.estado = 'entregado'
            pedido.save()
        elif pedido.estado == 'pendiente' and nuevo_estado == 'en preparación':
            pedido.estado = 'en preparación'
            pedido.save()
        else:
            return Response(
                {'error': 'Transición de estado no válida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(PedidoReadSerializer(pedido).data, status=status.HTTP_200_OK)

class PedidoListCreateAPIView(generics.ListCreateAPIView):
    queryset = Pedido.objects.all().order_by('-fecha_pedido')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PedidoReadSerializer
        return PedidoWriteSerializer

class PedidoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pedido.objects.all()
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PedidoReadSerializer
        return PedidoWriteSerializer
    
class DetallePedidoCreateAPIView(generics.CreateAPIView):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoWriteSerializer

class DetallePedidoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DetallePedido.objects.all()
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DetallePedidoReadSerializer
        return DetallePedidoWriteSerializer

class ClienteListCreateAPIView(generics.ListCreateAPIView):
    queryset = Cliente.objects.all().order_by('nombre')
    serializer_class = ClienteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            {
                'message': 'Cliente creado exitosamente',
                'cliente': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class PedidosPorFechaView(APIView):
    def get(self, request):
        fecha_str = request.GET.get('fecha')
        if not fecha_str:
            return Response(
                {'error': 'Parámetro fecha requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fecha = date.fromisoformat(fecha_str)
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pedidos = Pedido.objects.filter(fecha_entrega=fecha)
        serializer = PedidoReadSerializer(pedidos, many=True)  # ← Cambiado
        
        return Response({
            'fecha': fecha_str,
            'pedidos': serializer.data,
            'total': pedidos.count()
        })

class PedidosPorEstadoView(APIView):
    def get(self, request):
        estado = request.GET.get('estado')
        if not estado:
            return Response(
                {'error': 'Parámetro estado requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if estado not in dict(Pedido.ESTADO_PEDIDO):
            return Response(
                {'error': 'Estado no válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pedidos = Pedido.objects.filter(estado=estado)
        serializer = PedidoReadSerializer(pedidos, many=True)  # ← Cambiado
        
        return Response({
            'estado': estado,
            'pedidos': serializer.data,
            'total': pedidos.count()
        })
    
class IngredientesExtraCreateAPIView(generics.CreateAPIView):
    queryset = IngredientesExtra.objects.all()
    serializer_class = IngredientesExtraWriteSerializer  # ← Cambiado

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            {
                'message': 'Ingrediente extra agregado exitosamente',
                'ingrediente_extra': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class IngredientesExtraRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = IngredientesExtra.objects.all()
    serializer_class = IngredientesExtraWriteSerializer  # ← Cambiado
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return Response(
            {
                'message': 'Ingrediente extra eliminado exitosamente',
                'ingrediente_extra_id': instance.id
            },
            status=status.HTTP_204_NO_CONTENT
        )
    
class EliminarDetallesPedidoView(APIView):
    def delete(self, request, pk):
        try:
            pedido = Pedido.objects.get(pk=pk)
            # Eliminar todos los detalles del pedido (usando el related_name correcto)
            pedido.detalles.all().delete()  # ← Cambiado de detallepedido_set a detalles
            return Response(
                {'message': 'Detalles del pedido eliminados exitosamente'},
                status=status.HTTP_200_OK
            )
        except Pedido.DoesNotExist:
            return Response(
                {'error': 'Pedido no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )