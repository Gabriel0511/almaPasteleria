# admin.py - VERSIÓN ACTUALIZADA con HistorialStock y Perdida
from django.contrib import admin
from .models import Insumo, Proveedor, CategoriaInsumo, UnidadMedida, Perdida, HistorialStock

# --- ADMIN CLASSES SIMPLIFICADAS ---

class InsumoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'unidad_medida', 'stock_actual', 'stock_minimo', 'proveedor', 'activo']
    list_filter = ['categoria', 'unidad_medida', 'proveedor', 'activo']
    search_fields = ['nombre']
    list_editable = ['stock_actual', 'stock_minimo']

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'email']
    search_fields = ['nombre', 'email']

class CategoriaInsumoAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'abreviatura', 'es_unidad_base']
    search_fields = ['nombre', 'abreviatura']
    list_filter = ['es_unidad_base']

# --- NUEVOS MODELOS ---

class PerdidaAdmin(admin.ModelAdmin):
    list_display = ['insumo', 'cantidad', 'motivo', 'fecha']
    list_filter = ['motivo', 'fecha', 'insumo']
    search_fields = ['insumo__nombre', 'observaciones']
    date_hierarchy = 'fecha'
    
    def get_queryset(self, request):
        # Ordenar por fecha descendente por defecto
        return super().get_queryset(request).order_by('-fecha')

class HistorialStockAdmin(admin.ModelAdmin):
    list_display = ['insumo', 'tipo_movimiento', 'cantidad', 'unidad_medida', 'fecha']
    list_filter = ['tipo_movimiento', 'fecha', 'insumo']
    search_fields = ['insumo__nombre', 'descripcion']
    date_hierarchy = 'fecha'
    
    def get_queryset(self, request):
        # Ordenar por fecha descendente por defecto
        return super().get_queryset(request).order_by('-fecha')

# --- REGISTROS SIMPLES ---
admin.site.register(Insumo, InsumoAdmin)
admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(CategoriaInsumo, CategoriaInsumoAdmin)
admin.site.register(UnidadMedida, UnidadMedidaAdmin)
admin.site.register(Perdida, PerdidaAdmin)
admin.site.register(HistorialStock, HistorialStockAdmin)