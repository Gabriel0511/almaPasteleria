from django.urls import path
from .views import (
    RecetaListCreateAPIView,
    RecetaRetrieveUpdateDestroyAPIView,
    RecetaInsumoListCreateAPIView,
    RecetaInsumoRetrieveUpdateDestroyAPIView,
    IncrementarRecetaView,
    DecrementarRecetaView,
    RecetaInsumoPartialUpdateAPIView
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
]