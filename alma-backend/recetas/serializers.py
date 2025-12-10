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
        """Calcular costo de este insumo en la receta - VERSIÓN ULTRA SEGURA"""
        try:
            if not obj.insumo or not obj.insumo.precio_unitario:
                return "0.00"
            
            # 🔹 PASO 1: Convertir precio a FLOAT (GARANTIZADO)
            precio = self._convertir_a_float(obj.insumo.precio_unitario)
            
            # 🔹 PASO 2: Convertir cantidad a FLOAT (GARANTIZADO)
            cantidad = self._convertir_a_float(obj.cantidad)
            
            # 🔹 PASO 3: Verificar conversión de unidades
            if obj.unidad_medida and obj.insumo.unidad_medida:
                unidad_receta = obj.unidad_medida.abreviatura.lower()
                unidad_insumo = obj.insumo.unidad_medida.abreviatura.lower()
                
                if unidad_receta != unidad_insumo:
                    # 🔹 Convertir unidades (convertir_unidad ya devuelve float)
                    cantidad = convertir_unidad(cantidad, unidad_receta, unidad_insumo)
            
            # 🔹 PASO 4: Calcular costo (FLOAT * FLOAT = SEGURO)
            costo = precio * cantidad
            return f"{costo:.2f}"
            
        except Exception as e:
            print(f"❌ Error calculando costo para {obj.insumo.nombre if obj.insumo else 'insumo desconocido'}: {e}")
            return "0.00"
    
    def _convertir_a_float(self, valor):
        """Convertir cualquier tipo a float de forma segura"""
        if valor is None:
            return 0.0
        
        try:
            if isinstance(valor, Decimal):
                return float(valor)
            elif isinstance(valor, (int, float)):
                return float(valor)
            else:
                # Si es string, limpiar y convertir
                valor_str = str(valor).replace(',', '.')
                return float(valor_str)
        except:
            return 0.0
    
    class Meta:
        model = RecetaInsumo
        fields = ['id', 'insumo', 'cantidad', 'unidad_medida', 'costo_insumo']

class RecetaSerializer(serializers.ModelSerializer):
    insumos = RecetaInsumoSerializer(many=True, read_only=True)
    
    costo_total = serializers.SerializerMethodField()
    costo_unitario = serializers.SerializerMethodField()
    
    def get_costo_total(self, obj):
        """Calcular costo total - VERSIÓN ULTRA SEGURA"""
        try:
            costo_total = Decimal('0.00')
            
            for insumo_receta in obj.insumos.all():
                if not insumo_receta.insumo or not insumo_receta.insumo.precio_unitario:
                    continue
                
                # 🔹 Convertir usando el método seguro
                precio = self._convertir_a_float(insumo_receta.insumo.precio_unitario)
                cantidad = self._convertir_a_float(insumo_receta.cantidad)
                
                # 🔹 Verificar conversión de unidades
                if insumo_receta.unidad_medida and insumo_receta.insumo.unidad_medida:
                    unidad_receta = insumo_receta.unidad_medida.abreviatura.lower()
                    unidad_insumo = insumo_receta.insumo.unidad_medida.abreviatura.lower()
                    
                    if unidad_receta != unidad_insumo:
                        cantidad = convertir_unidad(cantidad, unidad_receta, unidad_insumo)
                
                # 🔹 Multiplicación segura
                costo_insumo = precio * cantidad
                costo_total += costo_insumo
            
            return f"{costo_total:.2f}"
            
        except Exception as e:
            print(f"❌ Error calculando costo total: {e}")
            return "0.00"
    
    def get_costo_unitario(self, obj):
        """Calcular costo unitario"""
        try:
            # Obtener costo total como Decimal
            costo_total_str = self.get_costo_total(obj)
            costo_total = Decimal(costo_total_str.replace(',', '.'))
            
            if obj.rinde > 0:
                costo_unitario = costo_total / Decimal(str(obj.rinde))
                return f"{costo_unitario:.2f}"
            return "0.00"
        except Exception as e:
            print(f"❌ Error calculando costo unitario: {e}")
            return "0.00"
    
    def _convertir_a_float(self, valor):
        """Método auxiliar para convertir a float"""
        if valor is None:
            return 0.0
        
        try:
            if isinstance(valor, Decimal):
                return float(valor)
            elif isinstance(valor, (int, float)):
                return float(valor)
            else:
                valor_str = str(valor).replace(',', '.')
                return float(valor_str)
        except:
            return 0.0
    
    def create(self, validated_data):
        """Crear receta y calcular costos - VERSIÓN SIMPLIFICADA"""
        try:
            print(f"🔧 Creando receta con datos validados: {validated_data}")
            
            # Establecer valores por defecto
            validated_data['costo_total'] = Decimal('0.00')
            validated_data['costo_unitario'] = Decimal('0.00')
            validated_data['veces_hecha'] = 0
            validated_data['veces_hecha_hoy'] = 0
            
            # Crear la receta
            receta = Receta.objects.create(**validated_data)
            print(f"✅ Receta creada exitosamente: {receta.id} - {receta.nombre}")
            
            return receta
        
    except Exception as e:
        print(f"❌ Error en create de RecetaSerializer: {e}")
        import traceback
        traceback.print_exc()
        raise serializers.ValidationError(f"Error al crear receta: {str(e)}")
    
    def update(self, instance, validated_data):
        """Actualizar receta y recalcular costos"""
        # Actualizar campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Recalcular costos después de actualizar
        self._actualizar_costos_receta(instance)
        
        return instance
    
    def _actualizar_costos_receta(self, receta):
        """Actualizar costos en la base de datos"""
        try:
            # Obtener costo total del serializer
            costo_total_str = self.get_costo_total(receta)
            costo_total = Decimal(costo_total_str.replace(',', '.'))
            
            # Calcular costo unitario
            if receta.rinde > 0:
                costo_unitario = costo_total / Decimal(str(receta.rinde))
            else:
                costo_unitario = Decimal('0.00')
            
            # Actualizar directamente en la base de datos
            Receta.objects.filter(pk=receta.pk).update(
                costo_total=costo_total,
                costo_unitario=costo_unitario
            )
            
            # Refrescar la instancia
            receta.refresh_from_db()
            
            print(f"✅ Costos actualizados para receta {receta.nombre}: Total=${costo_total}, Unitario=${costo_unitario}")
            
        except Exception as e:
            print(f"❌ Error actualizando costos para receta {receta.nombre}: {e}")
    
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