from django.db import models
from django.utils import timezone
from datetime import timedelta
from recetas.models import Receta
from insumos.models import Insumo, UnidadMedida

# Create your models here.
# --- CLIENTES ---
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

# --- PEDIDOS ---
class Pedido(models.Model):
    ESTADO_PEDIDO = [
        ('pendiente', 'Pendiente'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_pedido = models.DateField()
    fecha_entrega = models.DateField()
    fecha_fabricacion = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_PEDIDO, default='pendiente')

    # ELIMINAR el método save() - Dejar que Django maneje el guardado normal
    # La lógica de fecha_fabricacion se puede manejar en el serializer

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nombre}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.receta.nombre} x{self.cantidad}"

class IngredientesExtra(models.Model):
    detalle = models.ForeignKey(DetallePedido, on_delete=models.CASCADE, related_name='ingredientes_extra')
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.CASCADE)  # ← Quitado blank=True, null=True

    def __str__(self):
        return f"{self.insumo.nombre} ({self.cantidad} {self.unidad_medida.abreviatura if self.unidad_medida else 'N/A'})"