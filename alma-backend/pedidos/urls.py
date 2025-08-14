# urls.py
from django.urls import path
from .views import PedidosHoyView, ActualizarEstadoPedidoView

urlpatterns = [
    path('pedidos/hoy/', PedidosHoyView.as_view(), name='pedidos-hoy'),
        path('pedidos/<int:pk>/actualizar-estado/', ActualizarEstadoPedidoView.as_view(), name='actualizar-estado-pedido'),
]