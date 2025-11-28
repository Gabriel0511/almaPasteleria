# celery.py
from celery import Celery
from celery.schedules import crontab

app = Celery('tu_proyecto')

app.conf.beat_schedule = {
    'cierre-automatico-medianoche': {
        'task': 'recetas.tasks.tarea_cierre_automatico',
        'schedule': crontab(hour=0, minute=0),  # Ejecutar a las 00:00 UTC
    },
}