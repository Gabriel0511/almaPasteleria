from django.urls import path
from .views import (
    RecetaListCreateAPIView,
    RecetaRetrieveUpdateDestroyAPIView,
    RecetaInsumoListCreateAPIView,
    RecetaInsumoRetrieveUpdateDestroyAPIView,
    IncrementarRecetaView,
    DecrementarRecetaView,
    RecetaInsumoPartialUpdateAPIView,
    RecetasHechasHoyView,
    RecetasPorFechaView,
    GenerarPDFRecetasView,
    CierreDiarioView
)

urlpatterns = [
    path('recetas/', RecetaListCreateAPIView.as_view(), name='recetas-list'),
    path('recetas/<int:pk>/', RecetaRetrieveUpdateDestroyAPIView.as_view(), name='receta-detail'),
    path('recetas/<int:receta_id>/insumos/', RecetaInsumoListCreateAPIView.as_view(), name='receta-insumos-list'),
    path('recetas/<int:receta_id>/insumos/<int:pk>/', RecetaInsumoRetrieveUpdateDestroyAPIView.as_view(), name='receta-insumo-detail'),
    path('recetas/<int:pk>/incrementar/', IncrementarRecetaView.as_view(), name='incrementar-receta'),
    path('recetas/<int:pk>/decrementar/', DecrementarRecetaView.as_view()),
    path('recetas/<int:receta_id>/insumos/<int:pk>/actualizar/', 
     RecetaInsumoPartialUpdateAPIView.as_view(), 
     name='receta-insumo-actualizar'),
    path('recetas-hechas-hoy/', RecetasHechasHoyView.as_view(), name='recetas-hechas-hoy'),
    path('recetas-por-fecha/', RecetasPorFechaView.as_view(), name='recetas-por-fecha'),
    path('recetas-por-fecha/pdf/', GenerarPDFRecetasView.as_view(), name='recetas-por-fecha-pdf'),
    path('cierre-diario/', CierreDiarioView.as_view(), name='cierre-diario'),
    path('api/recetas/actualizar-costos/', views.ActualizarCostosRecetasView.as_view(), name='actualizar_costos_recetas'),
    path('api/recetas/<int:pk>/actualizar-costo/', views.ActualizarCostoRecetaView.as_view(), name='actualizar_costo_receta'),
]