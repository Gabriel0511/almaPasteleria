# En recetas/management/commands/probar_calculos.py
from django.core.management.base import BaseCommand
from recetas.models import Receta, RecetaInsumo
from decimal import Decimal

class Command(BaseCommand):
    help = 'Prueba los cálculos de costos'

    def handle(self, *args, **kwargs):
        recetas = Receta.objects.all()[:15]  # Probar solo las primeras 5
        
        for receta in recetas:
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"Receta: {receta.nombre}")
            self.stdout.write(f"Costo actual en BD: ${receta.costo_total}")
            self.stdout.write(f"{'-'*60}")
            
            total_calculado = Decimal('0.00')
            
            for insumo_receta in receta.insumos.all():
                try:
                    # Mostrar información del insumo
                    self.stdout.write(f"\nInsumo: {insumo_receta.insumo.nombre}")
                    self.stdout.write(f"  Cantidad: {insumo_receta.cantidad} {insumo_receta.unidad_medida.abreviatura}")
                    self.stdout.write(f"  Precio: ${insumo_receta.insumo.precio_unitario}/{insumo_receta.insumo.unidad_medida.abreviatura}")
                    
                    # Verificar tipos
                    cantidad_tipo = type(insumo_receta.cantidad)
                    precio_tipo = type(insumo_receta.insumo.precio_unitario)
                    self.stdout.write(f"  Tipo cantidad: {cantidad_tipo}")
                    self.stdout.write(f"  Tipo precio: {precio_tipo}")
                    
                    # Calcular usando el método
                    costo_insumo = insumo_receta.calcular_costo()
                    self.stdout.write(f"  Costo calculado: ${costo_insumo}")
                    
                    total_calculado += costo_insumo
                    
                except Exception as e:
                    self.stdout.write(f"  ✗ Error: {e}")
            
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"Total calculado: ${total_calculado}")
            self.stdout.write(f"Diferencia con BD: ${total_calculado - receta.costo_total}")