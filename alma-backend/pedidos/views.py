from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import date
from pedidos.models import Pedido
from django.shortcuts import get_object_or_404
from .serializers import PedidoSerializer

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