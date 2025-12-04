# admin.py - VERSIÓN COMPLETA para recetas
from django.contrib import admin
from .models import Receta, RecetaInsumo, HistorialReceta

# --- ADMIN CLASSES SIMPLIFICADAS ---

class RecetaInsumoInline(admin.TabularInline):
    model = RecetaInsumo
    extra = 1
    fields = ['insumo', 'cantidad', 'unidad_medida']
    autocomplete_fields = ['insumo']

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'veces_hecha', 'veces_hecha_hoy', 'rinde', 'unidad_rinde', 'costo_total', 'precio_venta', 'ultima_actualizacion_diaria']
    list_filter = ['unidad_rinde', 'ultima_actualizacion_diaria']
    search_fields = ['nombre']
    readonly_fields = ['veces_hecha', 'veces_hecha_hoy', 'costo_total', 'costo_unitario', 'creado_en', 'ultima_actualizacion_diaria']
    inlines = [RecetaInsumoInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('insumos')

@admin.register(RecetaInsumo)
class RecetaInsumoAdmin(admin.ModelAdmin):
    list_display = ['receta', 'insumo', 'cantidad', 'unidad_medida']
    list_filter = ['receta', 'insumo']
    search_fields = ['receta__nombre', 'insumo__nombre']
    autocomplete_fields = ['receta', 'insumo', 'unidad_medida']

@admin.register(HistorialReceta)
class HistorialRecetaAdmin(admin.ModelAdmin):
    list_display = ['receta', 'fecha_preparacion', 'cantidad_preparada']
    list_filter = ['receta', 'fecha_preparacion']
    search_fields = ['receta__nombre']
    date_hierarchy = 'fecha_preparacion'
    readonly_fields = ['fecha_preparacion']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-fecha_preparacion')