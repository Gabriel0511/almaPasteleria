from rest_framework import serializers
from .models import Receta, RecetaInsumo, Insumo, UnidadMedida
from decimal import Decimal

class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = ['id', 'nombre', 'abreviatura']

class InsumoSerializer(serializers.ModelSerializer):
    unidad_medida = UnidadMedidaSerializer()
    
    class Meta:
        model = Insumo
        fields = ['id', 'nombre', 'unidad_medida', 'stock_actual']

class DecimalConComaField(serializers.DecimalField):
    def to_representation(self, value):
        value = super().to_representation(value)
        if value is not None:
            return str(value).replace('.', ',')
        return value

class RecetaInsumoSerializer(serializers.ModelSerializer):
    insumo = InsumoSerializer()
    unidad_medida = UnidadMedidaSerializer()
    cantidad = DecimalConComaField(max_digits=10, decimal_places=3)
    
    class Meta:
        model = RecetaInsumo
        fields = ['id', 'insumo', 'cantidad', 'unidad_medida']

class RecetaSerializer(serializers.ModelSerializer):
    insumos = RecetaInsumoSerializer(many=True, read_only=True, source='recetainsumo_set')
    
    class Meta:
        model = Receta
        fields = ['id', 'nombre', 'veces_hecha', 'rinde', 'unidad_rinde', 
                 'costo_unitario', 'costo_total', 'precio_venta', 'creado_en', 'insumos']
        
class RecetaInsumoCreateSerializer(serializers.ModelSerializer):
    # Usar PrimaryKeyRelatedField para aceptar solo IDs
    insumo = serializers.PrimaryKeyRelatedField(queryset=Insumo.objects.all())
    unidad_medida = serializers.PrimaryKeyRelatedField(queryset=UnidadMedida.objects.all())
    
    class Meta:
        model = RecetaInsumo
        fields = ['id', 'insumo', 'cantidad', 'unidad_medida']
    
    def update(self, instance, validated_data):
        # Actualizar solo los campos permitidos
        instance.cantidad = validated_data.get('cantidad', instance.cantidad)
        instance.unidad_medida = validated_data.get('unidad_medida', instance.unidad_medida)
        instance.save()
        return instance