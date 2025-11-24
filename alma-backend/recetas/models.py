from django.db import models
from django.utils import timezone
from datetime import timedelta
from insumos.models import Insumo, UnidadMedida
from insumos.conversiones import convertir_unidad
from decimal import Decimal

class Receta(models.Model):
    UNIDADES_RINDE = [
        ('porciones', 'Porciones'),
        ('unidades', 'Unidades'),
    ]

    nombre = models.CharField(max_length=100)
    veces_hecha = models.PositiveIntegerField(default=0)  # Contador histórico total
    veces_hecha_hoy = models.PositiveIntegerField(default=0)  # ✅ NUEVO: Contador diario
    rinde = models.PositiveIntegerField()
    unidad_rinde = models.CharField(max_length=20, choices=UNIDADES_RINDE)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
    # ✅ NUEVO MÉTODO: Incrementar contador diario
    def incrementar_contador_diario(self):
        """Incrementa tanto el contador diario como el histórico"""
        self.veces_hecha_hoy += 1
        self.veces_hecha += 1
        # Crear registro en historial
        HistorialReceta.objects.create(
        receta=self,
        cantidad_preparada=1,
    )
        self.save()
    
    def decrementar_contador_diario(self):
        """Decrementa el contador diario y el histórico si es posible"""
        if self.veces_hecha_hoy > 0:
            self.veces_hecha_hoy -= 1
        if self.veces_hecha > 0:
            self.veces_hecha -= 1
        
        # Eliminar el registro más reciente del historial
        ultimo_historial = self.historial.order_by('-fecha_preparacion').first()
        if ultimo_historial:
            ultimo_historial.delete()
        
        self.save()
    
    # ✅ NUEVO MÉTODO: Reiniciar contador diario (para el cierre)
    def reiniciar_contador_diario(self):
        """Reinicia solo el contador diario (para cierre del día)"""
        self.veces_hecha_hoy = 0
        self.save(update_fields=['veces_hecha_hoy'])
    
    def calcular_costo_total(self):
        """Calcula el costo total sumando el costo de todos los insumos"""
        costo_total = Decimal('0.00')
        for insumo_receta in self.insumos.all():
            costo_insumo = insumo_receta.calcular_costo()
            costo_total += costo_insumo
        return costo_total
    
    def actualizar_costos(self):
        """Actualiza los costos sin guardar el objeto (para evitar recursión)"""
        self.costo_total = self.calcular_costo_total()
        if self.rinde and self.rinde > 0:
            self.costo_unitario = self.costo_total / Decimal(str(self.rinde))
        else:
            self.costo_unitario = Decimal('0.00')
        
        # Guardar solo si el objeto ya existe en la BD
        if self.pk:
            # Usar update para evitar recursión en save()
            Receta.objects.filter(pk=self.pk).update(
                costo_total=self.costo_total,
                costo_unitario=self.costo_unitario
            )
    
    def save(self, *args, **kwargs):
        # Si es un objeto nuevo, establecer valores por defecto
        if not self.pk:
            self.costo_total = Decimal('0.00')
            self.costo_unitario = Decimal('0.00')
        
        # Llamar al save original
        super().save(*args, **kwargs)
        
        # Si ya existe en la BD, actualizar costos después de guardar
        if self.pk:
            self.actualizar_costos()

class RecetaInsumo(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name='insumos')
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    unidad_medida = models.ForeignKey('insumos.UnidadMedida', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.insumo.nombre} en {self.receta.nombre}"
    
    def calcular_costo(self):
        """Calcula el costo de este insumo en la receta"""
        try:
            if not self.insumo.precio_unitario:
                return Decimal('0.00')
            
            # Obtener la cantidad en la unidad del insumo
            cantidad_en_unidad_insumo = self.get_cantidad_en_unidad_insumo()
            
            # Calcular costo
            costo = self.insumo.precio_unitario * cantidad_en_unidad_insumo
            return costo.quantize(Decimal('0.01'))  # Redondear a 2 decimales
            
        except Exception as e:
            print(f"❌ Error calculando costo para {self.insumo.nombre}: {e}")
            return Decimal('0.00')
    
    def save(self, *args, **kwargs):
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")
        if not self.insumo_id:
            raise ValueError("El insumo es requerido")
        if not self.unidad_medida_id:
            raise ValueError("La unidad de medida es requerida")
        
        super().save(*args, **kwargs)
        
        # Recalcular el costo de la receta cuando se guarda un insumo
        if self.receta:
            self.receta.actualizar_costos()
    
    def get_cantidad_en_unidad_insumo(self):
        """Convierte la cantidad a la unidad de medida del insumo"""
        try:
            # Asegurarse de que tenemos los objetos relacionados cargados
            if not hasattr(self, '_insumo_cache'):
                self.insumo = Insumo.objects.select_related('unidad_medida').get(pk=self.insumo_id)
            
            if not hasattr(self, '_unidad_medida_cache'):
                self.unidad_medida = UnidadMedida.objects.get(pk=self.unidad_medida_id)
            
            cantidad_decimal = Decimal(str(self.cantidad))
            unidad_receta = self.unidad_medida.abreviatura.lower()
            unidad_insumo = self.insumo.unidad_medida.abreviatura.lower()
            
            # Si las unidades coinciden, no hay conversión necesaria
            if unidad_receta == unidad_insumo:
                return cantidad_decimal
            
            # Usar conversiones.py
            try:
                cantidad_convertida = convertir_unidad(
                    cantidad_decimal, 
                    unidad_receta, 
                    unidad_insumo
                )
                return cantidad_convertida
            except ValueError as e:
                print(f"⚠️ No se pudo convertir {unidad_receta} a {unidad_insumo}: {e}")
                # Intentar con el sistema de factores
                try:
                    if (hasattr(self.unidad_medida, 'factor_conversion_base') and 
                        hasattr(self.insumo.unidad_medida, 'factor_conversion_base')):
                        
                        cantidad_base = cantidad_decimal * self.unidad_medida.factor_conversion_base
                        cantidad_convertida = cantidad_base / self.insumo.unidad_medida.factor_conversion_base
                        return cantidad_convertida
                except Exception as factor_error:
                    print(f"⚠️ Error en conversión por factores: {factor_error}")
                
                return cantidad_decimal
                    
        except Exception as e:
            print(f"❌ Error en get_cantidad_en_unidad_insumo: {e}")
            return Decimal(str(self.cantidad))  

class HistorialReceta(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name='historial')
    fecha_preparacion = models.DateTimeField(auto_now_add=True)
    cantidad_preparada = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.receta.nombre} - {self.fecha_preparacion.date()}"
    
    class Meta:
        ordering = ['-fecha_preparacion']  # Ordenar por fecha más reciente primero