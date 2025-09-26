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
    veces_hecha = models.PositiveIntegerField(default=0)
    rinde = models.PositiveIntegerField()
    unidad_rinde = models.CharField(max_length=20, choices=UNIDADES_RINDE)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class RecetaInsumo(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    unidad_medida = models.ForeignKey('insumos.UnidadMedida', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.insumo.nombre} en {self.receta.nombre}"
    
    def save(self, *args, **kwargs):
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")
        if not self.insumo_id:
            raise ValueError("El insumo es requerido")
        if not self.unidad_medida_id:
            raise ValueError("La unidad de medida es requerida")
        super().save(*args, **kwargs)
    
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