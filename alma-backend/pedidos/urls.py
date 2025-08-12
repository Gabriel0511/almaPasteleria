# urls.py
from django.urls import path
from .views import PedidosHoyView

urlpatterns = [
    path('pedidos/hoy/', PedidosHoyView.as_view(), name='pedidos-hoy'),
]