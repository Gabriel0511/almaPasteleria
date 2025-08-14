from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import date
from pedidos.models import Pedido
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