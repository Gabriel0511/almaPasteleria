# serializers.py
from rest_framework import serializers
from .models import Insumo, UnidadMedida, CategoriaInsumo

class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = ['nombre', 'abreviatura']

class CategoriaInsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaInsumo
        fields = ['nombre']

class InsumoSerializer(serializers.ModelSerializer):
    unidad_medida = UnidadMedidaSerializer()
    categoria = CategoriaInsumoSerializer()
    
    class Meta:
        model = Insumo
        fields = ['id', 'nombre', 'categoria', 'unidad_medida', 
                 'stock_actual', 'stock_minimo', 'necesita_reposicion']