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
        
        # Entregar hoy: pedidos con fecha_entrega = hoy
        entregar_hoy = Pedido.objects.filter(
            fecha_entrega=hoy,
            estado__in=['pendiente', 'listo']
        )
        
        # Hacer hoy: pedidos con fecha_entrega en los próximos 3 días (hoy+1, hoy+2, hoy+3)
        fecha_limite = hoy + timedelta(days=3)
        hacer_hoy = Pedido.objects.filter(
            fecha_entrega__range=[hoy + timedelta(days=1), fecha_limite],
            estado__in=['pendiente', 'listo']
        )
        
        entregar_serializer = PedidoReadSerializer(entregar_hoy, many=True)
        hacer_serializer = PedidoReadSerializer(hacer_hoy, many=True)
        
        return Response({
            'entregar_hoy': entregar_serializer.data,
            'hacer_hoy': hacer_serializer.data
        }, status=status.HTTP_200_OK)

class ActualizarEstadoPedidoView(APIView):
    def patch(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        nuevo_estado = request.data.get('estado')
        
        # Validar transición de estado
        if pedido.estado in ['pendiente', 'listo'] and nuevo_estado == 'entregado':
            pedido.estado = 'entregado'
            pedido.save()
        elif pedido.estado == 'pendiente' and nuevo_estado == 'listo':
            pedido.estado = 'listo'
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
    
    def perform_create(self, serializer):
        # Guardar la fecha exacta como viene del frontend
        fecha_entrega_str = self.request.data.get('fecha_entrega')
        if fecha_entrega_str:
            # Parsear la fecha sin conversión de zona horaria
            from datetime import datetime
            fecha_entrega = datetime.strptime(fecha_entrega_str, '%Y-%m-%d').date()
            serializer.save(fecha_entrega=fecha_entrega)
        else:
            serializer.save()

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
            pedido.detalles.all().delete()
            return Response(
                {'message': 'Detalles del pedido eliminados exitosamente'},
                status=status.HTTP_200_OK
            )
        except Pedido.DoesNotExist:
            return Response(
                {'error': 'Pedido no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
class PedidosEntregadosView(APIView):
    def get(self, request):
        # Obtener parámetros de fecha
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        
        # Filtrar solo pedidos entregados
        pedidos = Pedido.objects.filter(estado='entregado').order_by('-fecha_entrega')
        
        # Aplicar filtros de fecha si se proporcionan
        if fecha_inicio:
            try:
                fecha_inicio = date.fromisoformat(fecha_inicio)
                pedidos = pedidos.filter(fecha_entrega__gte=fecha_inicio)
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_inicio inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if fecha_fin:
            try:
                fecha_fin = date.fromisoformat(fecha_fin)
                pedidos = pedidos.filter(fecha_entrega__lte=fecha_fin)
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_fin inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = PedidoReadSerializer(pedidos, many=True)
        
        return Response({
            'pedidos': serializer.data,
            'total': pedidos.count(),
            'filtros': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            }
        })