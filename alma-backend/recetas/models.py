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
    ]

    nombre = models.CharField(max_length=100)
    veces_hecha = models.PositiveIntegerField(default=0)  # Nuevo campo
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
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)  # Cambiado a Decimal
    unidad_medida = models.ForeignKey('insumos.UnidadMedida', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.insumo.nombre} en {self.receta.nombre}"
    
    def save(self, *args, **kwargs):
        # Validar que la cantidad sea positiva
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")
        
        # Validar que el insumo y unidad de medida existan
        if not self.insumo_id:
            raise ValueError("El insumo es requerido")
        if not self.unidad_medida_id:
            raise ValueError("La unidad de medida es requerida")
        
        super().save(*args, **kwargs)
    
    def get_cantidad_en_unidad_insumo(self):
        """Devuelve la cantidad convertida a la unidad del insumo"""
        from insumos.conversiones import convertir_unidad
        
        # Verificar si las unidades son diferentes
        if self.unidad_medida.abreviatura == self.insumo.unidad_medida.abreviatura:
            return float(self.cantidad)
        
        try:
            cantidad_convertida = convertir_unidad(
                float(self.cantidad),
                self.unidad_medida.abreviatura.lower(),  # Usar minúsculas para consistencia
                self.insumo.unidad_medida.abreviatura.lower()
            )
            return float(cantidad_convertida)
        except (ValueError, TypeError, KeyError) as e:
            # Si hay error en la conversión, devolver la cantidad original
            print(f"Error en conversión de {self.unidad_medida.abreviatura} a {self.insumo.unidad_medida.abreviatura}: {e}")
            return float(self.cantidad)