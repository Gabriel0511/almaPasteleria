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
        """Convierte la cantidad a la unidad de medida del insumo usando conversiones.py"""
        try:
            # Verificar que los objetos relacionados existan
            if not hasattr(self, 'insumo') or not self.insumo:
                return self.cantidad
            if not hasattr(self, 'unidad_medida') or not self.unidad_medida:
                return self.insumo
            if not hasattr(self.insumo, 'unidad_medida') or not self.insumo.unidad_medida:
                return self.cantidad
                
            unidad_receta = self.unidad_medida.abreviatura.lower()
            unidad_insumo = self.insumo.unidad_medida.abreviatura.lower()
            
            # Si las unidades coinciden, devolver la cantidad original
            if unidad_receta == unidad_insumo:
                return self.cantidad
                
            # Usar el módulo de conversiones
            try:
                cantidad_convertida = convertir_unidad(
                    Decimal(str(self.cantidad)), 
                    unidad_receta, 
                    unidad_insumo
                )
                return cantidad_convertida
            except ValueError as e:
                # Si no hay conversión disponible, loggear y devolver cantidad original
                print(f"⚠️ No se pudo convertir {unidad_receta} a {unidad_insumo}: {e}")
                return self.cantidad
                
        except Exception as e:
            print(f"❌ Error en get_cantidad_en_unidad_insumo: {e}")
            return self.cantidad