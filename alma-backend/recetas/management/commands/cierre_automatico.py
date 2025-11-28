from django.core.management.base import BaseCommand
from django.utils import timezone
from recetas.models import Receta
import pytz

class Command(BaseCommand):
    help = 'Ejecuta cierre automático de recetas para nuevo día'
    
    def handle(self, *args, **options):
        try:
            tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
            ahora_argentina = timezone.now().astimezone(tz_argentina)
            
            self.stdout.write(f"🔹 Verificando cierre automático - Hora Argentina: {ahora_argentina}")
            
            recetas_procesadas = Receta.verificar_cierre_automatico()
            
            if recetas_procesadas > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Cierre automático ejecutado: {recetas_procesadas} recetas procesadas')
                )
            else:
                self.stdout.write('🔹 No se requiere cierre automático')
                
        except Exception as e:
            self.stderr.write(f'❌ Error en cierre automático: {str(e)}')