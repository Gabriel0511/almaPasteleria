# recetas/management/commands/recalcular_costos_recetas.py
from django.core.management.base import BaseCommand
from recetas.models import Receta
from django.db import transaction

class Command(BaseCommand):
    help = 'Recalcula los costos de todas las recetas'

    def handle(self, *args, **options):
        recetas = Receta.objects.all()
        total_recetas = recetas.count()
        recetas_actualizadas = 0
        
        self.stdout.write(f'Recalculando costos para {total_recetas} recetas...')
        
        for receta in recetas:
            try:
                with transaction.atomic():
                    # Forzar la actualización de costos
                    costo_anterior = receta.costo_total
                    receta.actualizar_costos()
                    receta.refresh_from_db()
                    
                    recetas_actualizadas += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Receta "{receta.nombre}": '
                            f'${costo_anterior} → ${receta.costo_total}'
                        )
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error en receta "{receta.nombre}": {e}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Proceso completado: {recetas_actualizadas}/{total_recetas} recetas actualizadas'
            )
        )