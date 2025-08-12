from django.urls import path
from .views import (
    RecetaListCreateAPIView,
    RecetaRetrieveUpdateDestroyAPIView,
    RecetaInsumoListCreateAPIView,
    RecetaInsumoRetrieveUpdateDestroyAPIView
)

urlpatterns = [
    path('recetas/', RecetaListCreateAPIView.as_view(), name='recetas-list'),
    path('recetas/<int:pk>/', RecetaRetrieveUpdateDestroyAPIView.as_view(), name='receta-detail'),
    path('recetas/<int:receta_id>/insumos/', RecetaInsumoListCreateAPIView.as_view(), name='receta-insumos-list'),
    path('recetas/<int:receta_id>/insumos/<int:pk>/', RecetaInsumoRetrieveUpdateDestroyAPIView.as_view(), name='receta-insumo-detail'),
]