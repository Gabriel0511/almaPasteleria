from django.urls import path
from . import views

urlpatterns = [
    path('estado/', views.obtener_estado_cierre_dia, name='estado_cierre_dia'),
    path('cerrar/', views.cerrar_dia_laboral, name='cerrar_dia_laboral'),
    path('historial/', views.obtener_historial_cierres, name='historial_cierres'),
    path('pre-reporte/', views.pre_reporte_diario, name='pre_reporte_diario'),
    path('reporte-pdf/', views.generar_reporte_diario_pdf, name='reporte_pdf'),
    path('recetas-por-fecha/', views.recetas_por_fecha, name='recetas_por_fecha'),
]