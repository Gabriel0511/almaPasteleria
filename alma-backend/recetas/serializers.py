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
        if (value is not None):
            return str(value).replace('.', ',')
        return value

class RecetaInsumoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecetaInsumo
        fields = ['insumo', 'cantidad', 'unidad_medida']

class RecetaInsumoSerializer(serializers.ModelSerializer):
    insumo = InsumoSerializer()
    unidad_medida = UnidadMedidaSerializer()
    cantidad = DecimalConComaField(max_digits=10, decimal_places=3)
    
    class Meta:
        model = RecetaInsumo
        fields = ['id', 'insumo', 'cantidad', 'unidad_medida']

class RecetaSerializer(serializers.ModelSerializer):
    insumos = RecetaInsumoSerializer(many=True, read_only=True, source='recetainsumo_set')
    # Agregar campo para crear/actualizar insumos
    receta_insumos = RecetaInsumoCreateSerializer(many=True, write_only=True, required=False)
    
    class Meta:
        model = Receta
        fields = ['id', 'nombre', 'veces_hecha', 'rinde', 'unidad_rinde', 
                 'costo_unitario', 'costo_total', 'precio_venta', 'creado_en', 
                 'insumos', 'receta_insumos']
        extra_kwargs = {
            'costo_unitario': {'required': False},
            'costo_total': {'required': False},
        }
    
    def create(self, validated_data):
        # Extraer los datos de insumos si están presentes
        insumos_data = validated_data.pop('receta_insumos', [])
        
        # Crear la receta
        receta = Receta.objects.create(**validated_data)
        
        # Crear los insumos de la receta
        for insumo_data in insumos_data:
            RecetaInsumo.objects.create(receta=receta, **insumo_data)
        
        # Calcular costos
        receta.calcular_costos()
        receta.save()
        
        return receta
    
    def update(self, instance, validated_data):
        # Extraer los datos de insumos si están presentes
        insumos_data = validated_data.pop('receta_insumos', [])
        
        # Actualizar los campos de la receta
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Eliminar insumos existentes y crear los nuevos
        if insumos_data:
            # Eliminar insumos existentes
            RecetaInsumo.objects.filter(receta=instance).delete()
            
            # Crear los nuevos insumos
            for insumo_data in insumos_data:
                RecetaInsumo.objects.create(receta=instance, **insumo_data)
        
        # Recalcular costos
        instance.calcular_costos()
        instance.save()
        
        return instance