# views.py - Versión completa para pedidos
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.utils import timezone
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from .models import Pedido, DetallePedido, Cliente, IngredientesExtra
from .serializers import PedidoSerializer, DetallePedidoSerializer, ClienteSerializer
from recetas.models import Receta
from insumos.models import Insumo

class PedidosHoyView(APIView):
    def get(self, request):
        hoy = date.today()
        
        # Pedidos para entregar hoy
        entregar_hoy = Pedido.objects.filter(
            fecha_entrega=hoy,
            estado__in=['pendiente', 'en preparación']
        )
        
        # Pedidos para fabricar hoy
        hacer_hoy = Pedido.objects.filter(
            fecha_fabricacion=hoy,
            estado__in=['pendiente', 'en preparación']
        )
        
        entregar_serializer = PedidoSerializer(entregar_hoy, many=True)
        hacer_serializer = PedidoSerializer(hacer_hoy, many=True)
        
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
        
        return Response(PedidoSerializer(pedido).data, status=status.HTTP_200_OK)

class PedidoListCreateAPIView(generics.ListCreateAPIView):
    queryset = Pedido.objects.all().order_by('-fecha_pedido')
    serializer_class = PedidoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            {
                'message': 'Pedido creado exitosamente',
                'pedido': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class PedidoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                'message': 'Pedido actualizado exitosamente',
                'pedido': serializer.data
            }
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return Response(
            {
                'message': 'Pedido eliminado exitosamente',
                'pedido_id': instance.id
            },
            status=status.HTTP_204_NO_CONTENT
        )

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

class DetallePedidoCreateAPIView(generics.CreateAPIView):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            {
                'message': 'Detalle de pedido agregado exitosamente',
                'detalle': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class DetallePedidoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return Response(
            {
                'message': 'Detalle de pedido eliminado exitosamente',
                'detalle_id': instance.id
            },
            status=status.HTTP_204_NO_CONTENT
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
        serializer = PedidoSerializer(pedidos, many=True)
        
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
        serializer = PedidoSerializer(pedidos, many=True)
        
        return Response({
            'estado': estado,
            'pedidos': serializer.data,
            'total': pedidos.count()
        })