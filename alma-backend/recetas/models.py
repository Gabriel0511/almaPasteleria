from django.db import models
from django.utils import timezone
from datetime import timedelta
from insumos.models import Insumo, UnidadMedida

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
    cantidad = models.PositiveIntegerField()
    unidad_medida = models.ForeignKey('insumos.UnidadMedida', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.insumo.nombre} en {self.receta.nombre}"
