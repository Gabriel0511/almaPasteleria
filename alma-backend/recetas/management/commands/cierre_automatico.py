from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from recetas.models import Receta, HistorialReceta
import pytz
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Ejecuta cierre automático de recetas para el día anterior a las 23:59'
    
    def handle(self, *args, **options):
        try:
            tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
            ahora_argentina = timezone.now().astimezone(tz_argentina)
            
            # Obtener la fecha de ayer (para cerrar el día anterior)
            ayer_argentina = ahora_argentina - timedelta(days=1)
            fecha_cierre = ayer_argentina.date()
            
            self.stdout.write(f"🔹 Verificando cierre automático - Hora Argentina: {ahora_argentina}")
            self.stdout.write(f"🔹 Cerrando recetas del día: {fecha_cierre}")
            
            # Obtener recetas con actividad del día anterior
            recetas_con_actividad = Receta.objects.filter(veces_hecha_hoy__gt=0)
            
            if not recetas_con_actividad.exists():
                self.stdout.write('🔹 No hay recetas con actividad para cerrar')
                return
            
            total_preparaciones = 0
            
            with transaction.atomic():
                for receta in recetas_con_actividad:
                    if receta.veces_hecha_hoy > 0:
                        # Crear fecha de preparación como ayer a las 23:59 EN UTC
                        fecha_preparacion_arg = datetime.combine(
                            fecha_cierre, 
                            datetime.min.time()
                        ).replace(hour=23, minute=59, second=59)
                        fecha_preparacion_arg = tz_argentina.localize(fecha_preparacion_arg)
                        
                        # Convertir a UTC para almacenar en BD
                        fecha_preparacion_utc = fecha_preparacion_arg.astimezone(pytz.UTC)
                        
                        # Crear historial con fecha UTC
                        HistorialReceta.objects.create(
                            receta=receta,
                            cantidad_preparada=receta.veces_hecha_hoy,
                            fecha_preparacion=fecha_preparacion_utc  # ✅ Guardar en UTC
                        )
                        
                        total_preparaciones += receta.veces_hecha_hoy
                        
                        # Reiniciar contador
                        receta.veces_hecha_hoy = 0
                        receta.ultima_actualizacion_diaria = fecha_cierre
                        receta.save(update_fields=['veces_hecha_hoy', 'ultima_actualizacion_diaria'])
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Cierre automático ejecutado: {len(recetas_con_actividad)} recetas procesadas')
            )
            self.stdout.write(f'   📊 Total preparaciones: {total_preparaciones}')
            self.stdout.write(f'   📅 Fecha cerrada: {fecha_cierre}')
            self.stdout.write(f'   ⏰ Fechas guardadas en UTC: {fecha_preparacion_utc}')
                
        except Exception as e:
            self.stderr.write(f'❌ Error en cierre automático: {str(e)}')
            import traceback
            self.stderr.write(f'❌ Traceback: {traceback.format_exc()}')