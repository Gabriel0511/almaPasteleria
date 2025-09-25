from django.db import models
from django.utils import timezone
from datetime import timedelta
from insumos.models import Insumo, UnidadMedida
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
        """Versión simplificada para debug"""
        print("✅ get_cantidad_en_unidad_insumo llamado")  # Debug
        try:
            # Verificar que los objetos relacionados existan
            if not hasattr(self, 'insumo') or not self.insumo:
                print("❌ Insumo no disponible")
                return self.cantidad
            if not hasattr(self, 'unidad_medida') or not self.unidad_medida:
                print("❌ Unidad medida no disponible")
                return self.cantidad
                
            print(f"🔍 Unidad receta: {self.unidad_medida.abreviatura}")
            print(f"🔍 Unidad insumo: {self.insumo.unidad_medida.abreviatura}")
            
            # Si las unidades coinciden, devolver la cantidad original
            if self.unidad_medida.abreviatura == self.insumo.unidad_medida.abreviatura:
                print("✅ Unidades iguales, retornando cantidad original")
                return self.cantidad
                
            print("🔄 Unidades diferentes, necesitaría conversión")
            # Por ahora devolver la cantidad original
            return self.cantidad
            
        except Exception as e:
            print(f"❌ Error en get_cantidad_en_unidad_insumo: {e}")
            return self.cantidad