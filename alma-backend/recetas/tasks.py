# tasks.py (en tu app de recetas)
from celery import shared_task
from django.utils import timezone
from recetas.models import Receta
import pytz

@shared_task
def tarea_cierre_automatico():
    """Tarea programada para cierre automático"""
    try:
        tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
        ahora_argentina = timezone.now().astimezone(tz_argentina)
        
        print(f"🔹 Tarea cierre automático ejecutada: {ahora_argentina}")
        
        return Receta.verificar_cierre_automatico()
    except Exception as e:
        print(f"❌ Error en tarea cierre automático: {e}")
        return 0