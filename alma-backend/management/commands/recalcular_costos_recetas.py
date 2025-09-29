# management/commands/recalcular_costos_recetas.py
from django.core.management.base import BaseCommand
from recetas.models import Receta

class Command(BaseCommand):
    help = 'Recalcula los costos de todas las recetas'

    def handle(self, *args, **options):
        recetas = Receta.objects.all()
        for receta in recetas:
            receta.actualizar_costos()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Receta "{receta.nombre}": ${receta.costo_total}'
                )
            )