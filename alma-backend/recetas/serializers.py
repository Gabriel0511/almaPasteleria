from rest_framework import serializers
from .models import Receta, RecetaInsumo, Insumo, UnidadMedida
from decimal import Decimal
from insumos.conversiones import convertir_unidad

class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = ['id', 'nombre', 'abreviatura']

class InsumoSerializer(serializers.ModelSerializer):
    unidad_medida = UnidadMedidaSerializer()
    
    class Meta:
        model = Insumo
        fields = ['id', 'nombre', 'unidad_medida', 'stock_actual', 'precio_unitario']

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
    
    costo_insumo = serializers.SerializerMethodField()
    
    def get_costo_insumo(self, obj):
        """Calcular costo de este insumo en la receta"""
        try:
            if not obj.insumo or not obj.insumo.precio_unitario:
                return "0.00"
            
            # Convertir precio a float
            precio_str = str(obj.insumo.precio_unitario).replace(',', '.')
            precio = float(precio_str)
            
            # Convertir cantidad a float
            cantidad_str = str(obj.cantidad).replace(',', '.')
            cantidad = float(cantidad_str)
            
            # Verificar si necesitamos conversión de unidades
            if obj.unidad_medida and obj.insumo.unidad_medida:
                unidad_receta = obj.unidad_medida.abreviatura.lower()
                unidad_insumo = obj.insumo.unidad_medida.abreviatura.lower()
                
                if unidad_receta != unidad_insumo:
                    # Usar la función convertir_unidad (ahora devuelve float)
                    cantidad = convertir_unidad(cantidad, unidad_receta, unidad_insumo)
            
            # Calcular costo (float * float)
            costo = precio * cantidad
            return f"{costo:.2f}"
            
        except Exception as e:
            print(f"⚠️ Error calculando costo insumo: {e}")
            return "0.00"
    
    class Meta:
        model = RecetaInsumo
        fields = ['id', 'insumo', 'cantidad', 'unidad_medida', 'costo_insumo']

class RecetaSerializer(serializers.ModelSerializer):
    insumos = RecetaInsumoSerializer(many=True, read_only=True)
    
    costo_total = serializers.SerializerMethodField()
    costo_unitario = serializers.SerializerMethodField()
    
    def get_costo_total(self, obj):
        """Calcular costo total de la receta dinámicamente"""
        try:
            costo_total = 0.0
            
            for insumo_receta in obj.insumos.all():
                if not insumo_receta.insumo or not insumo_receta.insumo.precio_unitario:
                    continue
                
                # Convertir precio a float
                precio_str = str(insumo_receta.insumo.precio_unitario).replace(',', '.')
                precio = float(precio_str)
                
                # Convertir cantidad a float
                cantidad_str = str(insumo_receta.cantidad).replace(',', '.')
                cantidad = float(cantidad_str)
                
                # Verificar conversión de unidades
                if insumo_receta.unidad_medida and insumo_receta.insumo.unidad_medida:
                    unidad_receta = insumo_receta.unidad_medida.abreviatura.lower()
                    unidad_insumo = insumo_receta.insumo.unidad_medida.abreviatura.lower()
                    
                    if unidad_receta != unidad_insumo:
                        cantidad = convertir_unidad(cantidad, unidad_receta, unidad_insumo)
                
                costo_insumo = precio * cantidad
                costo_total += costo_insumo
            
            return f"{costo_total:.2f}"
            
        except Exception as e:
            print(f"⚠️ Error calculando costo total: {e}")
            return "0.00"
    
    def get_costo_unitario(self, obj):
        """Calcular costo unitario"""
        try:
            costo_total_str = self.get_costo_total(obj)
            costo_total = float(costo_total_str)
            
            if obj.rinde > 0:
                costo_unitario = costo_total / float(obj.rinde)
                return f"{costo_unitario:.2f}"
            return "0.00"
        except Exception as e:
            print(f"⚠️ Error calculando costo unitario: {e}")
            return "0.00"
    
    class Meta:
        model = Receta
        fields = ['id', 'nombre', 'veces_hecha', 'veces_hecha_hoy', 'rinde', 'unidad_rinde', 
                  'costo_unitario', 'costo_total', 'precio_venta', 'creado_en', 'insumos']
        read_only_fields = ['costo_unitario', 'costo_total']

class RecetaInsumoCreateSerializer(serializers.ModelSerializer):
    insumo = serializers.PrimaryKeyRelatedField(queryset=Insumo.objects.all())
    unidad_medida = serializers.PrimaryKeyRelatedField(queryset=UnidadMedida.objects.all())
    
    class Meta:
        model = RecetaInsumo
        fields = ['id', 'insumo', 'cantidad', 'unidad_medida']
    
    def update(self, instance, validated_data):
        instance.cantidad = validated_data.get('cantidad', instance.cantidad)
        instance.unidad_medida = validated_data.get('unidad_medida', instance.unidad_medida)
        instance.save()
        return instance
    
    def create(self, validated_data):
        return super().create(validated_data)