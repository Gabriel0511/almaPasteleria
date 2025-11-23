# cierre_diario/models.py - CORREGIR
from django.db import models
from django.conf import settings  # ✅ IMPORTAR settings
from pedidos.models import Pedido
from recetas.models import Receta
from insumos.models import Insumo

class HistorialCierreDia(models.Model):
    fecha = models.DateField(unique=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ✅ CAMBIADO: Usar AUTH_USER_MODEL
        on_delete=models.CASCADE
    )
    recetas_registradas = models.IntegerField(default=0)
    pedidos_registrados = models.IntegerField(default=0)
    insumos_registrados = models.IntegerField(default=0)
    fecha_cierre = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cierre_dia_historial'
        verbose_name = 'Historial de Cierre Diario'
        verbose_name_plural = 'Historiales de Cierres Diarios'

class HistorialRecetasDia(models.Model):
    cierre_dia = models.ForeignKey(HistorialCierreDia, on_delete=models.CASCADE, related_name='recetas')
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    cantidad_preparada = models.IntegerField(default=0)
    empleado = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ✅ CAMBIADO: Usar AUTH_USER_MODEL
        on_delete=models.SET_NULL, 
        null=True
    )
    
    class Meta:
        db_table = 'cierre_dia_recetas'

class HistorialPedidosDia(models.Model):
    cierre_dia = models.ForeignKey(HistorialCierreDia, on_delete=models.CASCADE, related_name='pedidos')
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    cliente_nombre = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'cierre_dia_pedidos'

class HistorialInsumosUtilizados(models.Model):
    cierre_dia = models.ForeignKey(HistorialCierreDia, on_delete=models.CASCADE, related_name='insumos')
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    cantidad_utilizada = models.DecimalField(max_digits=10, decimal_places=3)
    motivo = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'cierre_dia_insumos'