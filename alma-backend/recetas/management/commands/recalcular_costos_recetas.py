# En recetas/management/commands/recalcular_costos.py
from django.core.management.base import BaseCommand
from recetas.models import Receta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Recalcula los costos de todas las recetas'

    def handle(self, *args, **kwargs):
        recetas = Receta.objects.all()
        total_recetas = recetas.count()
        actualizadas = 0
        
        self.stdout.write(f"Recalculando costos para {total_recetas} recetas...")
        
        for receta in recetas:
            try:
                costo_anterior = receta.costo_total
                receta.costo_total = receta.calcular_costo_total()
                
                if receta.rinde and receta.rinde > 0:
                    receta.costo_unitario = receta.costo_total / Decimal(str(receta.rinde))
                else:
                    receta.costo_unitario = Decimal('0.00')
                
                # Guardar si hubo cambios
                if costo_anterior != receta.costo_total:
                    receta.save(update_fields=['costo_total', 'costo_unitario'])
                    actualizadas += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ {receta.nombre}: ${costo_anterior} → ${receta.costo_total}")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Error en {receta.nombre}: {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Proceso completado. {actualizadas}/{total_recetas} recetas actualizadas.")
        )