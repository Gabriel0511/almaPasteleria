from rest_framework import serializers
from .models import Receta, RecetaInsumo, Insumo, UnidadMedida

class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = ['id', 'nombre', 'abreviatura']

class InsumoSerializer(serializers.ModelSerializer):
    unidad_medida = UnidadMedidaSerializer()
    
    class Meta:
        model = Insumo
        fields = ['id', 'nombre', 'unidad_medida', 'stock_actual']

class RecetaInsumoSerializer(serializers.ModelSerializer):
    insumo = InsumoSerializer()
    unidad_medida = UnidadMedidaSerializer()
    
    class Meta:
        model = RecetaInsumo
        fields = ['id', 'insumo', 'cantidad', 'unidad_medida']

class RecetaSerializer(serializers.ModelSerializer):
    insumos = RecetaInsumoSerializer(many=True, read_only=True, source='recetainsumo_set')
    
    class Meta:
        model = Receta
        fields = ['id', 'nombre', 'veces_hecha', 'rinde', 'unidad_rinde', 
                 'costo_unitario', 'costo_total', 'creado_en', 'insumos']