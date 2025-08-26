from django.contrib import admin
from .models import Insumo, Proveedor, CategoriaInsumo, UnidadMedida

# --- ADMIN CLASSES SIMPLIFICADAS ---
class InsumoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'unidad_medida', 'stock_actual', 'stock_minimo', 'proveedor']
    list_filter = ['categoria', 'unidad_medida', 'proveedor']
    search_fields = ['nombre']
    list_editable = ['stock_actual', 'stock_minimo']

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'email']
    search_fields = ['nombre', 'email']

class CategoriaInsumoAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'abreviatura']
    search_fields = ['nombre', 'abreviatura']

# --- REGISTROS SIMPLES ---
admin.site.register(Insumo, InsumoAdmin)
admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(CategoriaInsumo, CategoriaInsumoAdmin)
admin.site.register(UnidadMedida, UnidadMedidaAdmin)