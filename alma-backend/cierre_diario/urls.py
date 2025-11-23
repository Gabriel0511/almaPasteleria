from django.urls import path
from . import views

urlpatterns = [
    path('estado/', views.obtener_estado_cierre_dia, name='estado_cierre_dia'),
    path('cerrar/', views.cerrar_dia_laboral, name='cerrar_dia_laboral'),
    path('historial/', views.obtener_historial_cierres, name='historial_cierres'),
]