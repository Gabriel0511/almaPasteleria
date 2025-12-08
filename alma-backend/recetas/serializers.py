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
        """Calcular costo de este insumo en la receta - VERSIÓN SUPER SEGURA"""
        try:
            if not obj.insumo or not obj.insumo.precio_unitario:
                return "0.00"
            
            # 🔹 PASO 1: Convertir precio a FLOAT (no Decimal)
            precio_str = str(obj.insumo.precio_unitario)
            precio_str = precio_str.replace(',', '.')
            precio_float = float(precio_str)
            
            # 🔹 PASO 2: Convertir cantidad a FLOAT (no Decimal)
            cantidad_str = str(obj.cantidad)
            cantidad_str = cantidad_str.replace(',', '.')
            cantidad_float = float(cantidad_str)
            
            # 🔹 PASO 3: Verificar si necesitamos conversión de unidades
            if obj.unidad_medida and obj.insumo.unidad_medida:
                unidad_receta = obj.unidad_medida.abreviatura.lower()
                unidad_insumo = obj.insumo.unidad_medida.abreviatura.lower()
                
                if unidad_receta != unidad_insumo:
                    # 🔹 PASO CRÍTICO: Asegurar que convertir_unidad devuelva float
                    try:
                        cantidad_convertida = convertir_unidad(
                            cantidad_float,
                            unidad_receta,
                            unidad_insumo
                        )
                        # 🔹 FORZAR a float por si acaso
                        cantidad_float = float(str(cantidad_convertida))
                    except Exception as conv_error:
                        print(f"⚠️ Error en conversión: {conv_error}")
                        # Si falla la conversión, usar cantidad original
            
            # 🔹 PASO 4: Calcular costo (FLOAT * FLOAT = seguro)
            costo = precio_float * cantidad_float
            
            # 🔹 PASO 5: Formatear resultado
            return f"{costo:.2f}"
            
        except Exception as e:
            print(f"❌ ERROR CRÍTICO en get_costo_insumo: {str(e)}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return "0.00"
    
    class Meta:
        model = RecetaInsumo
        fields = ['id', 'insumo', 'cantidad', 'unidad_medida', 'costo_insumo']

class RecetaSerializer(serializers.ModelSerializer):
    insumos = RecetaInsumoSerializer(many=True, read_only=True)
    
    costo_total = serializers.SerializerMethodField()
    costo_unitario = serializers.SerializerMethodField()
    
    def get_costo_total(self, obj):
        """Calcular costo total - SIN Decimal, solo float"""
        try:
            costo_total_float = 0.0
            
            for insumo_receta in obj.insumos.all():
                if not insumo_receta.insumo or not insumo_receta.insumo.precio_unitario:
                    continue
                
                # 🔹 CONVERTIR a float explícitamente
                try:
                    precio_str = str(insumo_receta.insumo.precio_unitario)
                    precio_str = precio_str.replace(',', '.')
                    precio_float = float(precio_str)
                except:
                    precio_float = 0.0
                
                try:
                    cantidad_str = str(insumo_receta.cantidad)
                    cantidad_str = cantidad_str.replace(',', '.')
                    cantidad_float = float(cantidad_str)
                except:
                    cantidad_float = 0.0
                
                # 🔹 Conversión de unidades (si aplica)
                if insumo_receta.unidad_medida and insumo_receta.insumo.unidad_medida:
                    unidad_receta = insumo_receta.unidad_medida.abreviatura.lower()
                    unidad_insumo = insumo_receta.insumo.unidad_medida.abreviatura.lower()
                    
                    if unidad_receta != unidad_insumo:
                        try:
                            cantidad_float = convertir_unidad(
                                cantidad_float,
                                unidad_receta,
                                unidad_insumo
                            )
                            cantidad_float = float(str(cantidad_float))  # 🔹 FORZAR float
                        except:
                            pass  # Si falla, seguir con cantidad original
                
                # 🔹 Multiplicación SEGURA (float * float)
                costo_insumo = precio_float * cantidad_float
                costo_total_float += costo_insumo
            
            return f"{costo_total_float:.2f}"
            
        except Exception as e:
            print(f"❌ ERROR en get_costo_total: {str(e)}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return "0.00"
    
    def get_costo_unitario(self, obj):
        """Calcular costo unitario"""
        try:
            costo_total_str = self.get_costo_total(obj)
            costo_total_float = float(costo_total_str)
            
            if obj.rinde > 0:
                costo_unitario = costo_total_float / float(obj.rinde)
                return f"{costo_unitario:.2f}"
            return "0.00"
        except Exception as e:
            print(f"❌ ERROR en get_costo_unitario: {e}")
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