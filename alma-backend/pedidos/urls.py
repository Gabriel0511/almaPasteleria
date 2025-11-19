# urls.py - Versión completa actualizada
from django.urls import path
from .views import (
    PedidosHoyView,
    ActualizarEstadoPedidoView,
    PedidoListCreateAPIView,
    PedidoRetrieveUpdateDestroyAPIView,
    ClienteListCreateAPIView,
    DetallePedidoCreateAPIView,
    DetallePedidoRetrieveUpdateDestroyAPIView,
    PedidosPorFechaView,
    PedidosPorEstadoView,
    IngredientesExtraCreateAPIView,
    IngredientesExtraRetrieveUpdateDestroyAPIView,
    EliminarDetallesPedidoView,
    PedidosEntregadosView,
)

urlpatterns = [
    # Pedidos
    path('pedidos/', PedidoListCreateAPIView.as_view(), name='pedidos-list-create'),
    path('pedidos/<int:pk>/', PedidoRetrieveUpdateDestroyAPIView.as_view(), name='pedidos-detail'),
    path('pedidos/hoy/', PedidosHoyView.as_view(), name='pedidos-hoy'),
    path('pedidos/por-fecha/', PedidosPorFechaView.as_view(), name='pedidos-por-fecha'),
    path('pedidos/por-estado/', PedidosPorEstadoView.as_view(), name='pedidos-por-estado'),
    path('pedidos/<int:pk>/actualizar-estado/', ActualizarEstadoPedidoView.as_view(), name='actualizar-estado-pedido'),
    path('pedidos/<int:pk>/detalles/', EliminarDetallesPedidoView.as_view(), name='eliminar-detalles-pedido'),
    
    # Clientes
    path('clientes/', ClienteListCreateAPIView.as_view(), name='clientes-list-create'),
    
    # Detalles de pedido
    path('detalles-pedido/', DetallePedidoCreateAPIView.as_view(), name='detalles-pedido-create'),
    path('detalles-pedido/<int:pk>/', DetallePedidoRetrieveUpdateDestroyAPIView.as_view(), name='detalles-pedido-detail'),

    # Ingredientes extra - Nuevos endpoints
    path('ingredientes-extra/', IngredientesExtraCreateAPIView.as_view(), name='ingredientes-extra-create'),
    path('ingredientes-extra/<int:pk>/', IngredientesExtraRetrieveUpdateDestroyAPIView.as_view(), name='ingredientes-extra-detail'),

    # Pedidos entregados
    path('pedidos/entregados/', PedidosEntregadosView.as_view(), name='pedidos-entregados'),
]