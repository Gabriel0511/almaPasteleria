from django.db import models
from django.utils import timezone
from datetime import timedelta

# --- UNIDADES DE MEDIDA ---
class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    abreviatura = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    es_unidad_base = models.BooleanField(default=False)
    factor_conversion_base = models.DecimalField(max_digits=10, decimal_places=6, default=1.0)
    unidad_base = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"
    
    def convertir_a(self, cantidad, unidad_destino):
        """
        Convierte una cantidad de esta unidad a otra unidad
        """
        try:
            # Si es la misma unidad, no hay conversión
            if self == unidad_destino:
                return cantidad
            
            # Convertir a unidad base primero
            if self.es_unidad_base:
                cantidad_base = cantidad
            else:
                cantidad_base = cantidad * self.factor_conversion_base
            
            # Convertir de base a destino
            if unidad_destino.es_unidad_base:
                return cantidad_base
            else:
                return cantidad_base / unidad_destino.factor_conversion_base
                
        except Exception as e:
            print(f"Error en conversión de unidades: {e}")
            # Fallback: devolver la cantidad original
            return cantidad

# --- PROVEEDORES ---
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    
# --- CATEGORIAS DE INSUMOS ---
class CategoriaInsumo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Categoría de Insumo"
        verbose_name_plural = "Categorías de Insumos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

# --- INSUMOS ---
class Insumo(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(
        CategoriaInsumo,
        on_delete=models.PROTECT,
        null=True,  # Permite valores nulos
        blank=True,  # Opcional para el admin
        verbose_name="Categoria de insumo"
    )
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=3)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=3)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
    @property
    def necesita_reposicion(self):
        return self.stock_actual < self.stock_minimo
    
    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
        ordering = ['nombre']

# --- PÉRDIDAS DE STOCK ---
class Perdida(models.Model):
    MOTIVOS_CHOICES = [
        ('deterioro', 'Deterioro'),
        ('vencimiento', 'Vencimiento'),
        ('rotura', 'Rotura'),
        ('error', 'Error en registro'),
        ('uso_interno', 'Uso interno'),
        ('otro', 'Otro'),
    ]
    
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='perdidas')
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    motivo = models.CharField(max_length=50, choices=MOTIVOS_CHOICES)
    observaciones = models.TextField(blank=True, null=True)
    fecha = models.DateField(default=timezone.now)
    
    class Meta:
        verbose_name = "Pérdida de Stock"
        verbose_name_plural = "Pérdidas de Stock"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.insumo.nombre} - {self.cantidad} - {self.get_motivo_display()}"
    
    def save(self, *args, **kwargs):
        # Antes de guardar, actualizar el stock del insumo
        if not self.pk:  # Solo si es un nuevo registro (no actualización)
            self.insumo.stock_actual -= self.cantidad
            self.insumo.save()
        super().save(*args, **kwargs)

class HistorialStock(models.Model):
    TIPOS_MOVIMIENTO = [
        ('RECETA', 'Preparación de Receta'),
        ('INGREDIENTE_EXTRA', 'Ingrediente Extra en Pedido'),
        ('AJUSTE', 'Ajuste Manual'),
        ('COMPRA', 'Compra/Reposición'),
        ('PERDIDA', 'Pérdida'), 
    ]
    
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='historial')
    tipo_movimiento = models.CharField(max_length=20, choices=TIPOS_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)
    es_temporal = models.BooleanField(default=False)
    
    # Referencias opcionales
    receta = models.ForeignKey('recetas.Receta', on_delete=models.SET_NULL, null=True, blank=True)
    pedido = models.ForeignKey('pedidos.Pedido', on_delete=models.SET_NULL, null=True, blank=True)
    perdida = models.ForeignKey('Perdida', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.insumo.nombre} - {self.tipo_movimiento} - {self.cantidad}"