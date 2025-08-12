from django.urls import path
from . import views

urlpatterns = [
    path('insumos/', views.InsumoListAPIView.as_view(), name='insumos-list'),
    # Puedes añadir más rutas relacionadas con insumos aquí
]