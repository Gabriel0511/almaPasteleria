# serializers.py - Versión actualizada
from datetime import date
from rest_framework import serializers
from pedidos.models import Pedido, DetallePedido, Cliente, IngredientesExtra
from recetas.models import Receta
from insumos.models import Insumo, UnidadMedida

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'telefono', 'direccion']

class RecetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receta
        fields = ['id', 'nombre']

class InsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumo
        fields = ['id', 'nombre']

class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = ['id', 'nombre', 'abreviatura']

class IngredientesExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientesExtra
        fields = ['id', 'insumo', 'cantidad', 'UnidadMedida']

class DetallePedidoSerializer(serializers.ModelSerializer):
    receta = RecetaSerializer(read_only=True)
    receta_id = serializers.PrimaryKeyRelatedField(
        queryset=Receta.objects.all(),
        source='receta',
        write_only=True,
        required=True
    )
    ingredientes_extra = IngredientesExtraSerializer(many=True, required=False)
    
    class Meta:
        model = DetallePedido
        fields = ['id', 'receta', 'receta_id', 'cantidad', 'observaciones', 'ingredientes_extra']

class PedidoSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        source='cliente',
        write_only=True,
        required=True
    )
    detalles = DetallePedidoSerializer(many=True, source='detallepedido_set', required=False)
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'cliente', 'cliente_id', 'fecha_pedido', 'fecha_entrega',
            'fecha_fabricacion', 'estado', 'detalles'
        ]
        read_only_fields = ['fecha_fabricacion']

    def validate_fecha_entrega(self, value):
        if value < date.today():
            raise serializers.ValidationError("La fecha de entrega no puede ser en el pasado")
        return value

    def validate(self, data):
        fecha_entrega = data.get('fecha_entrega')
        fecha_pedido = data.get('fecha_pedido', date.today())
        
        if fecha_entrega and fecha_pedido:
            if fecha_entrega < fecha_pedido:
                raise serializers.ValidationError("La fecha de entrega no puede ser anterior a la fecha de pedido")
        
        return data

    def create(self, validated_data):
        detalles_data = validated_data.pop('detallepedido_set', [])
        pedido = Pedido.objects.create(**validated_data)
        
        for detalle_data in detalles_data:
            ingredientes_data = detalle_data.pop('ingredientes_extra', [])
            detalle = DetallePedido.objects.create(pedido=pedido, **detalle_data)
            
            for ingrediente_data in ingredientes_data:
                IngredientesExtra.objects.create(detalle=detalle, **ingrediente_data)
        
        return pedido

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detallepedido_set', None)
        
        # Actualizar campos del pedido
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar detalles si se proporcionan
        if detalles_data is not None:
            # Eliminar detalles existentes y crear nuevos
            instance.detallepedido_set.all().delete()
            
            for detalle_data in detalles_data:
                ingredientes_data = detalle_data.pop('ingredientes_extra', [])
                detalle = DetallePedido.objects.create(pedido=instance, **detalle_data)
                
                for ingrediente_data in ingredientes_data:
                    IngredientesExtra.objects.create(detalle=detalle, **ingrediente_data)
        
        return instance