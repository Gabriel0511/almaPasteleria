# serializers.py - Versión actualizada
from rest_framework import serializers
from .models import Insumo, UnidadMedida, CategoriaInsumo, Proveedor

class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = ['id', 'nombre', 'abreviatura']

class CategoriaInsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaInsumo
        fields = ['id', 'nombre']

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre']

class DecimalConComaField(serializers.DecimalField):
    def to_representation(self, value):
        value = super().to_representation(value)
        if value is not None:
            return str(value).replace('.', ',')
        return value

    def to_internal_value(self, data):
        # Convertir coma a punto para base de datos
        if isinstance(data, str):
            data = data.replace(',', '.')
        return super().to_internal_value(data)

class InsumoSerializer(serializers.ModelSerializer):
    unidad_medida = UnidadMedidaSerializer(read_only=True)
    categoria = CategoriaInsumoSerializer(read_only=True)
    proveedor = ProveedorSerializer(read_only=True)
    
    # Campos para escritura (creación/actualización)
    unidad_medida_id = serializers.PrimaryKeyRelatedField(
        queryset=UnidadMedida.objects.all(),
        source='unidad_medida',
        write_only=True,
        required=True
    )
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaInsumo.objects.all(),
        source='categoria',
        write_only=True,
        required=False,
        allow_null=True
    )
    proveedor_id = serializers.PrimaryKeyRelatedField(
        queryset=Proveedor.objects.all(),
        source='proveedor',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    stock_actual = DecimalConComaField(max_digits=10, decimal_places=3)
    stock_minimo = DecimalConComaField(max_digits=10, decimal_places=3)
    precio_unitario = DecimalConComaField(
        max_digits=10, 
        decimal_places=2, 
        required=False, 
        allow_null=True
    )
    
    class Meta:
        model = Insumo
        fields = [
            'id', 'nombre', 'categoria', 'categoria_id',
            'unidad_medida', 'unidad_medida_id', 
            'stock_actual', 'stock_minimo', 'precio_unitario',
            'proveedor', 'proveedor_id', 'activo',
            'fecha_actualizacion', 'necesita_reposicion'
        ]
        read_only_fields = ['fecha_actualizacion', 'necesita_reposicion']

    def validate_stock_actual(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock actual no puede ser negativo")
        return value

    def validate_stock_minimo(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock mínimo no puede ser negativo")
        return value

    def validate(self, data):
        # Validación personalizada si es necesario
        stock_actual = data.get('stock_actual')
        stock_minimo = data.get('stock_minimo')
        
        if stock_actual is not None and stock_minimo is not None:
            if stock_actual < stock_minimo:
                # Solo warning, no error
                pass
                
        return data