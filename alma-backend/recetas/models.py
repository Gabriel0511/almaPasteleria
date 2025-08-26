from django.db import models
from django.utils import timezone
from datetime import timedelta
from insumos.models import Insumo, UnidadMedida
from decimal import Decimal

# Create your models here.
# --- RECETAS ---
class Receta(models.Model):
    UNIDADES_RINDE = [
        ('porciones', 'Porciones'),
        ('unidades', 'Unidades'),
        ('entera', 'Entera'),
    ]

    nombre = models.CharField(max_length=100)
    veces_hecha = models.PositiveIntegerField(default=0)  # Nuevo campo
    rinde = models.PositiveIntegerField()
    unidad_rinde = models.CharField(max_length=20, choices=UNIDADES_RINDE)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class RecetaInsumo(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)  # Cambiado a Decimal
    unidad_medida = models.ForeignKey('insumos.UnidadMedida', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.insumo.nombre} en {self.receta.nombre}"
    
    def save(self, *args, **kwargs):
        from insumos.conversiones import convertir_unidad
        
        # Si la unidad de medida es diferente a la del insumo, convertir
        if self.unidad_medida != self.insumo.unidad_medida:
            try:
                # Convertir a la unidad del insumo para cálculos internos
                cantidad_convertida = convertir_unidad(
                    self.cantidad,
                    self.unidad_medida.abreviatura,
                    self.insumo.unidad_medida.abreviatura
                )
                # Guardamos la cantidad original pero manejamos conversiones en los métodos
                super().save(*args, **kwargs)
            except ValueError as e:
                raise ValueError(f"Error de conversión: {e}")
        else:
            super().save(*args, **kwargs)
    
    def get_cantidad_en_unidad_insumo(self):
        """Devuelve la cantidad convertida a la unidad del insumo"""
        from insumos.conversiones import convertir_unidad
        
        if self.unidad_medida == self.insumo.unidad_medida.abreviatura:
            return self.cantidad
        
        return convertir_unidad(
            self.cantidad,
            self.unidad_medida.abreviatura,
            self.insumo.unidad_medida.abreviatura
        )