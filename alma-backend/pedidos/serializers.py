# serializers.py - Versión corregida
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
        fields = ['id', 'nombre', 'veces_hecha', 'rinde', 'unidad_rinde', 
                 'costo_unitario', 'costo_total', 'precio_venta', 'creado_en']

class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = ['id', 'nombre', 'abreviatura']

class InsumoSerializer(serializers.ModelSerializer):
    unidad_medida = UnidadMedidaSerializer(read_only=True)
    
    class Meta:
        model = Insumo
        fields = ['id', 'nombre', 'unidad_medida', 'precio_unitario']

class IngredientesExtraReadSerializer(serializers.ModelSerializer):
    insumo = InsumoSerializer(read_only=True)
    unidad_medida = UnidadMedidaSerializer(read_only=True)

    class Meta:
        model = IngredientesExtra
        fields = ['id', 'insumo', 'cantidad', 'unidad_medida']

class IngredientesExtraWriteSerializer(serializers.ModelSerializer):
    insumo_id = serializers.PrimaryKeyRelatedField(
        queryset=Insumo.objects.all(),
        source='insumo',
        write_only=True,
        required=True
    )
    unidad_medida_id = serializers.PrimaryKeyRelatedField(
        queryset=UnidadMedida.objects.all(),
        source='unidad_medida',
        write_only=True,
        required=True
    )
    detalle_id = serializers.PrimaryKeyRelatedField(  # ✅ Campo agregado
        queryset=DetallePedido.objects.all(),
        source='detalle',
        write_only=True,
        required=True
    )

    class Meta:
        model = IngredientesExtra
        fields = ['id', 'insumo_id', 'cantidad', 'unidad_medida_id', 'detalle_id']

    def validate(self, data):
        insumo = data.get('insumo')
        unidad_medida = data.get('unidad_medida')
        
        if insumo and unidad_medida:
            grupos_compatibles = {
                'peso': ['kg', 'g', 'mg'],
                'volumen': ['l', 'ml', 'cl'],
                'unidad': ['u', 'pz', 'unidad']
            }
            
            grupo_insumo = None
            grupo_seleccionada = None
            
            for grupo, unidades in grupos_compatibles.items():
                if insumo.unidad_medida.abreviatura.lower() in unidades:
                    grupo_insumo = grupo
                if unidad_medida.abreviatura.lower() in unidades:
                    grupo_seleccionada = grupo
            
            if grupo_insumo != grupo_seleccionada:
                raise serializers.ValidationError(
                    f"La unidad {unidad_medida.abreviatura} no es compatible con {insumo.unidad_medida.abreviatura}"
                )
        
        return data

    def create(self, validated_data):
        insumo = validated_data['insumo']
        cantidad = validated_data['cantidad']
        unidad_seleccionada = validated_data['unidad_medida']
        
        if unidad_seleccionada != insumo.unidad_medida:
            try:
                cantidad_convertida = unidad_seleccionada.convertir_a(cantidad, insumo.unidad_medida)
                validated_data['cantidad'] = cantidad_convertida
            except Exception as e:
                # Si falla la conversión, mantener la cantidad original
                pass
        
        return super().create(validated_data)

class DetallePedidoReadSerializer(serializers.ModelSerializer):
    receta = RecetaSerializer(read_only=True)
    ingredientes_extra = IngredientesExtraReadSerializer(many=True, required=False)

    class Meta:
        model = DetallePedido
        fields = [
            'id', 'receta', 'cantidad', 'observaciones', 'ingredientes_extra'
        ]

class DetallePedidoWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    receta_id = serializers.PrimaryKeyRelatedField(
        queryset=Receta.objects.all(),
        source='receta',
        write_only=True,
        required=True
    )
    ingredientes_extra = IngredientesExtraWriteSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = DetallePedido
        fields = [
            'id', 'receta_id', 'cantidad', 'observaciones', 
            'ingredientes_extra', 'pedido'
        ]
        extra_kwargs = {
            'pedido': {'write_only': True}
        }

class PedidoReadSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    detalles = DetallePedidoReadSerializer(many=True, required=False)
    total = serializers.SerializerMethodField()
    recetas = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = [
            'id', 'cliente', 'fecha_pedido', 'fecha_entrega',
            'fecha_fabricacion', 'estado', 'detalles', 'total', 'receta'
        ]

    def get_total(self, obj):
       return obj.total
    
    def get_recetas(self, obj):
        """Obtener las recetas del pedido formateadas"""
        recetas = []
        for detalle in obj.detalles.all():
            receta_info = {
                'nombre': detalle.receta.nombre,
                'cantidad': detalle.cantidad,
                'observaciones': detalle.observaciones
            }
            recetas.append(receta_info)
        return recetas

class PedidoWriteSerializer(serializers.ModelSerializer):
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        source='cliente',
        write_only=True,
        required=True
    )
    detalles = DetallePedidoWriteSerializer(many=True, required=False)

    class Meta:
        model = Pedido
        fields = [
            'id', 'cliente_id', 'fecha_pedido', 'fecha_entrega',
            'fecha_fabricacion', 'estado', 'detalles'
        ]
        read_only_fields = ['fecha_fabricacion']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        pedido = Pedido.objects.create(**validated_data)

        for detalle_data in detalles_data:
            ingredientes_data = detalle_data.pop('ingredientes_extra', [])
            detalle = DetallePedido.objects.create(pedido=pedido, **detalle_data)

            for ingrediente_data in ingredientes_data:
                # Añadir el detalle_id al ingrediente_data
                ingrediente_data['detalle_id'] = detalle.id
                IngredientesExtra.objects.create(**ingrediente_data)

        return pedido

    def update(self, instance, validated_data):  # ← CORREGIDO: Ahora está dentro de la clase
        detalles_data = validated_data.pop('detalles', [])
        
        # actualizar campos del pedido
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        existing_detalles = {d.id: d for d in instance.detalles.all()}
        sent_detalles_ids = []

        for detalle_data in detalles_data:
            ingredientes_data = detalle_data.pop('ingredientes_extra', [])
            detalle_id = detalle_data.get("id")

            if detalle_id and detalle_id in existing_detalles:
                detalle = existing_detalles[detalle_id]
                for attr, value in detalle_data.items():
                    setattr(detalle, attr, value)
                detalle.save()
                sent_detalles_ids.append(detalle_id)
            else:
                detalle = DetallePedido.objects.create(pedido=instance, **detalle_data)

            existing_ing = {i.id: i for i in detalle.ingredientes_extra.all()}
            sent_ing_ids = []

            for ing_data in ingredientes_data:
                ing_id = ing_data.get("id")
                if ing_id and ing_id in existing_ing:
                    ing = existing_ing[ing_id]
                    for attr, value in ing_data.items():
                        setattr(ing, attr, value)
                    ing.save()
                    sent_ing_ids.append(ing_id)
                else:
                    # Añadir el detalle_id al ing_data
                    ing_data['detalle_id'] = detalle.id
                    IngredientesExtra.objects.create(**ing_data)

            # eliminar ingredientes que ya no están
            for ing_id, ing in existing_ing.items():
                if ing_id not in sent_ing_ids:
                    ing.delete()

        # eliminar detalles que ya no están
        for detalle_id, detalle in existing_detalles.items():
            if detalle_id not in sent_detalles_ids:
                detalle.delete()

        return instance