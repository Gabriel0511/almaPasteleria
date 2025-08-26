# urls.py - Versión actualizada
from django.urls import path
from . import views

urlpatterns = [
    # GET - Listar todos los insumos
    path('insumos/', views.InsumoListAPIView.as_view(), name='insumos-list'),
    
    # POST - Crear nuevo insumo
    path('insumos/crear/', views.InsumoCreateAPIView.as_view(), name='insumos-create'),
    
    # GET - Obtener un insumo específico
    path('insumos/<int:id>/', views.InsumoRetrieveAPIView.as_view(), name='insumos-detail'),
    
    # PUT - Actualizar insumo completo
    path('insumos/<int:id>/actualizar/', views.InsumoUpdateAPIView.as_view(), name='insumos-update'),
    
    # PATCH - Actualización parcial
    path('insumos/<int:id>/actualizar-parcial/', views.InsumoPartialUpdateAPIView.as_view(), name='insumos-partial-update'),
    
    # DELETE - Soft delete (marcar como inactivo)
    path('insumos/<int:id>/eliminar/', views.InsumoDestroyAPIView.as_view(), name='insumos-delete'),
    
    # DELETE - Eliminación permanente (cuidado)
    path('insumos/<int:id>/eliminar-permanentemente/', views.InsumoHardDeleteAPIView.as_view(), name='insumos-hard-delete'),
]