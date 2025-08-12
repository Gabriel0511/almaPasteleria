from rest_framework import serializers
from pedidos.models import Pedido, DetallePedido, Cliente
from recetas.models import Receta

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'telefono']

class RecetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receta
        fields = ['id', 'nombre']

class DetallePedidoSerializer(serializers.ModelSerializer):
    receta = RecetaSerializer()
    
    class Meta:
        model = DetallePedido
        fields = ['id', 'receta', 'cantidad', 'observaciones']

class PedidoSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer()
    detalles = DetallePedidoSerializer(many=True, source='detallepedido_set')
    
    class Meta:
        model = Pedido
        fields = ['id', 'cliente', 'fecha_pedido', 'fecha_entrega', 
                 'fecha_fabricacion', 'estado', 'detalles']