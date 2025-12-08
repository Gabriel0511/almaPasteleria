from rest_framework import serializers
from .models import Receta, RecetaInsumo, Insumo, UnidadMedida
from decimal import Decimal
from insumos.conversiones import convertir_unidad  # Importar la función de conversión

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
    
    # 🔹 AGREGAR: Calcular costo de este insumo dinámicamente
    costo_insumo = serializers.SerializerMethodField()
    
    def get_costo_insumo(self, obj):
        """Calcular costo de este insumo en la receta"""
        try:
            if not obj.insumo or not obj.insumo.precio_unitario:
                return Decimal('0.00')
            
            # Obtener precio unitario del insumo
            precio_unitario = Decimal(str(obj.insumo.precio_unitario))
            
            # Variable para la cantidad a calcular
            cantidad_para_calcular = Decimal(str(obj.cantidad))
            
            if obj.unidad_medida and obj.insumo.unidad_medida:
                unidad_receta = obj.unidad_medida.abreviatura.lower()
                unidad_insumo = obj.insumo.unidad_medida.abreviatura.lower()
                
                if unidad_receta != unidad_insumo:
                    # Convertir cantidad a la unidad del insumo
                    cantidad_float = float(obj.cantidad)
                    cantidad_convertida_float = convertir_unidad(
                        cantidad_float,
                        unidad_receta,
                        unidad_insumo
                    )
                    # Convertir el resultado float a Decimal
                    cantidad_para_calcular = Decimal(str(cantidad_convertida_float))
            
            # Calcular costo
            costo = precio_unitario * cantidad_para_calcular
            return costo.quantize(Decimal('0.01'))
            
        except Exception as e:
            print(f"Error calculando costo insumo: {e}")
            return Decimal('0.00')
    
    class Meta:
        model = RecetaInsumo
        fields = ['id', 'insumo', 'cantidad', 'unidad_medida', 'costo_insumo']

class RecetaSerializer(serializers.ModelSerializer):
    insumos = RecetaInsumoSerializer(many=True, read_only=True)
    
    # 🔹 CAMBIO IMPORTANTE: Hacer estos campos calculados dinámicamente
    costo_total = serializers.SerializerMethodField()
    costo_unitario = serializers.SerializerMethodField()
    
    def get_costo_total(self, obj):
        """Calcular costo total de la receta dinámicamente (sin guardar automáticamente)"""
        try:
            costo_total = Decimal('0.00')
            
            # Calcular sumando el costo de cada insumo
            for insumo_receta in obj.insumos.all():
                if not insumo_receta.insumo or not insumo_receta.insumo.precio_unitario:
                    continue
                
                precio_unitario = Decimal(str(insumo_receta.insumo.precio_unitario))
                cantidad_para_calcular = Decimal(str(insumo_receta.cantidad))
                
                if insumo_receta.unidad_medida and insumo_receta.insumo.unidad_medida:
                    unidad_receta = insumo_receta.unidad_medida.abreviatura.lower()
                    unidad_insumo = insumo_receta.insumo.unidad_medida.abreviatura.lower()
                    
                    if unidad_receta != unidad_insumo:
                        # Convertir cantidad
                        cantidad_float = float(insumo_receta.cantidad)
                        cantidad_convertida_float = convertir_unidad(
                            cantidad_float,
                            unidad_receta,
                            unidad_insumo
                        )
                        cantidad_para_calcular = Decimal(str(cantidad_convertida_float))
                
                costo_insumo = precio_unitario * cantidad_para_calcular
                costo_total += costo_insumo
            
            # 🔹 OPCIÓN: Descomenta esto si quieres actualizar la base de datos
            # Solo comenté esto para mejorar rendimiento
            # if obj.costo_total != costo_total:
            #     obj.costo_total = costo_total
            #     obj.costo_unitario = costo_total / Decimal(str(obj.rinde)) if obj.rinde > 0 else Decimal('0.00')
            #     obj.save(update_fields=['costo_total', 'costo_unitario'])
            
            return costo_total.quantize(Decimal('0.01'))
            
        except Exception as e:
            print(f"Error calculando costo total: {e}")
            return Decimal('0.00')
    
    def get_costo_unitario(self, obj):
        """Calcular costo unitario dinámicamente"""
        try:
            costo_total = self.get_costo_total(obj)
            if obj.rinde > 0:
                costo_unitario = costo_total / Decimal(str(obj.rinde))
                return costo_unitario.quantize(Decimal('0.01'))
            return Decimal('0.00')
        except Exception as e:
            print(f"Error calculando costo unitario: {e}")
            return Decimal('0.00')
    
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
        
        # 🔹 ACTUALIZAR: Recalcular costos de la receta después de modificar un insumo
        instance.receta.actualizar_costos()
        
        return instance
    
    def create(self, validated_data):
        instance = super().create(validated_data)
        
        # 🔹 ACTUALIZAR: Recalcular costos de la receta después de agregar un insumo
        instance.receta.actualizar_costos()
        
        return instance