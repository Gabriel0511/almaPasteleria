# urls.py - Versión actualizada
from django.urls import path
from . import views
from .views import UnidadMedidaListAPIView, UnidadMedidaDetailAPIView, UnidadMedidaCreateAPIView , CategoriaInsumoListAPIView, ProveedorListAPIView, ProveedorCreateAPIView, CategoriaInsumoCreateAPIView

urlpatterns = [
    # GET - Listar todos los insumos
    path('insumos/', views.InsumoListAPIView.as_view(), name='insumos-list'),
    
    # POST - Crear nuevo insumo
    path('insumos/crear/', views.InsumoCreateAPIView.as_view(), name='insumos-create'),
    
    # GET - Obtener un insumo específico
    path('insumos/<int:id>/', views.InsumoRetrieveAPIView.as_view(), name='insumos-detail'),
    
    # PUT - Actualizar insumo completo
    path('insumos/<int:id>/actualizar/', views.InsumoUpdateAPIView.as_view(), name='insumos-update'),
    path('insumos/<int:id>/actualizar-parcial/', views.InsumoPartialUpdateAPIView.as_view(), name='insumos-partial-update'),
    
    # DELETE - Soft delete (marcar como inactivo)
    path('insumos/<int:id>/eliminar/', views.InsumoDestroyAPIView.as_view(), name='insumos-delete'),
    
    # DELETE - Eliminación permanente (cuidado)
    path('insumos/<int:id>/eliminar-permanentemente/', views.InsumoHardDeleteAPIView.as_view(), name='insumos-hard-delete'),

    path('unidades-medida/', UnidadMedidaListAPIView.as_view(), name='unidades-medida-list'),
    path('unidades-medida/<int:pk>/', UnidadMedidaDetailAPIView.as_view(), name='unidades-medida-detail'),
    path('unidades-medida/crear/', UnidadMedidaCreateAPIView.as_view(), name='unidades-medidas-create'),

    # Rutas para categorías
    path('categorias/', CategoriaInsumoListAPIView.as_view(), name='categorias-list'),
    path('categorias/crear/', CategoriaInsumoCreateAPIView.as_view(), name='categorias-create'),
    
 # Rutas para Unidad Mediad
    path('Unidades/', CategoriaInsumoListAPIView.as_view(), name='categorias-list'),
    path('categorias/crear/', CategoriaInsumoCreateAPIView.as_view(), name='categorias-create'),

    # Rutas para proveedores - CORREGIDAS
    path('proveedores/', ProveedorListAPIView.as_view(), name='proveedores-list'),
    path('proveedores/crear/', ProveedorCreateAPIView.as_view(), name='proveedores-create'),
]