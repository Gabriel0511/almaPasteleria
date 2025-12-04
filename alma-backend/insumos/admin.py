# admin.py - Versión completa y mejorada
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from .models import Insumo, Proveedor, CategoriaInsumo, UnidadMedida, Perdida, HistorialStock

# --- FILTROS PERSONALIZADOS ---
class NecesitaReposicionFilter(admin.SimpleListFilter):
    title = '¿Necesita reposición?'
    parameter_name = 'necesita_reposicion'
    
    def lookups(self, request, model_admin):
        return (
            ('si', 'Sí, necesita reposición'),
            ('no', 'No necesita reposición'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'si':
            return queryset.filter(stock_actual__lt=F('stock_minimo'))
        if self.value() == 'no':
            return queryset.filter(stock_actual__gte=F('stock_minimo'))
        return queryset

class EstadoInsumoFilter(admin.SimpleListFilter):
    title = 'Estado'
    parameter_name = 'activo'
    
    def lookups(self, request, model_admin):
        return (
            ('activo', 'Activos'),
            ('inactivo', 'Inactivos'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'activo':
            return queryset.filter(activo=True)
        if self.value() == 'inactivo':
            return queryset.filter(activo=False)
        return queryset

# --- ACCIONES PERSONALIZADAS ---
def reactivar_insumos(modeladmin, request, queryset):
    queryset.update(activo=True)
    modeladmin.message_user(request, f"{queryset.count()} insumos reactivados exitosamente.")
reactivar_insumos.short_description = "Reactivar insumos seleccionados"

def desactivar_insumos(modeladmin, request, queryset):
    queryset.update(activo=False)
    modeladmin.message_user(request, f"{queryset.count()} insumos desactivados exitosamente.")
desactivar_insumos.short_description = "Desactivar insumos seleccionados"

def recalcular_necesita_reposicion(modeladmin, request, queryset):
    for insumo in queryset:
        # Esta propiedad se calcula automáticamente, pero podemos forzar un save
        insumo.save()  # Esto actualizará fecha_actualizacion también
    modeladmin.message_user(request, f"Estado de reposición recalculado para {queryset.count()} insumos.")
recalcular_necesita_reposicion.short_description = "Recalcular necesidad de reposición"

# --- INLINE PARA PÉRDIDAS ---
class PerdidaInline(admin.TabularInline):
    model = Perdida
    extra = 0
    fields = ['fecha', 'cantidad', 'motivo', 'observaciones']
    readonly_fields = ['fecha']
    
    def has_add_permission(self, request, obj=None):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True

# --- INLINE PARA HISTORIAL DE STOCK ---
class HistorialStockInline(admin.TabularInline):
    model = HistorialStock
    extra = 0
    max_num = 10  # Mostrar solo los últimos 10 registros
    fields = ['fecha', 'tipo_movimiento', 'cantidad', 'descripcion']
    readonly_fields = fields
    ordering = ['-fecha']
    
    def has_add_permission(self, request, obj=None):
        return False  # No permitir agregar desde aquí
    
    def has_delete_permission(self, request, obj=None):
        return False  # No permitir eliminar desde aquí

# --- ADMIN CLASS PARA INSUMOS ---
@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    # Campos para mostrar en la lista
    list_display = [
        'nombre_display', 
        'categoria', 
        'unidad_medida', 
        'stock_actual_display', 
        'stock_minimo_display', 
        'necesita_reposicion_display',
        'proveedor',
        'activo_display',
        'fecha_actualizacion_display'
    ]
    
    # Campos editables directamente en la lista
    list_editable = ['stock_actual', 'stock_minimo']
    
    # Campos para búsqueda
    search_fields = ['nombre', 'categoria__nombre', 'proveedor__nombre']
    
    # Filtros
    list_filter = [
        NecesitaReposicionFilter,
        EstadoInsumoFilter,
        'categoria',
        'unidad_medida',
        'proveedor',
    ]
    
    # Acciones personalizadas
    actions = [
        reactivar_insumos,
        desactivar_insumos,
        recalcular_necesita_reposicion
    ]
    
    # Campos en el formulario de edición
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'categoria', 'unidad_medida', 'proveedor')
        }),
        ('Stock y Precio', {
            'fields': (
                ('stock_actual', 'stock_minimo'), 
                'precio_unitario'
            )
        }),
        ('Estado', {
            'fields': ('activo',),
            'classes': ('collapse',)
        }),
        ('Información de Sistema', {
            'fields': ('fecha_actualizacion',),
            'classes': ('collapse',)
        }),
    )
    
    # Inlines
    inlines = [PerdidaInline, HistorialStockInline]
    
    # Campos de solo lectura
    readonly_fields = ['fecha_actualizacion']
    
    # Ordenamiento por defecto
    ordering = ['nombre']
    
    # Número de elementos por página
    list_per_page = 50
    
    # Campos para mostrar en el formulario de búsqueda avanzada
    autocomplete_fields = ['categoria', 'proveedor', 'unidad_medida']
    
    # Métodos personalizados para display
    def nombre_display(self, obj):
        return format_html('<strong>{}</strong>', obj.nombre)
    nombre_display.short_description = 'Nombre'
    nombre_display.admin_order_field = 'nombre'
    
    def stock_actual_display(self, obj):
        color = 'red' if obj.necesita_reposicion else 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.3f} {}</span>',
            color,
            obj.stock_actual,
            obj.unidad_medida.abreviatura
        )
    stock_actual_display.short_description = 'Stock Actual'
    stock_actual_display.admin_order_field = 'stock_actual'
    
    def stock_minimo_display(self, obj):
        return format_html(
            '{:.3f} {}',
            obj.stock_minimo,
            obj.unidad_medida.abreviatura
        )
    stock_minimo_display.short_description = 'Stock Mínimo'
    stock_minimo_display.admin_order_field = 'stock_minimo'
    
    def necesita_reposicion_display(self, obj):
        if obj.necesita_reposicion:
            return format_html(
                '<span style="color: white; background-color: red; padding: 2px 6px; border-radius: 3px; font-weight: bold;">SÍ</span>'
            )
        else:
            return format_html(
                '<span style="color: white; background-color: green; padding: 2px 6px; border-radius: 3px; font-weight: bold;">NO</span>'
            )
    necesita_reposicion_display.short_description = '¿Reponer?'
    necesita_reposicion_display.admin_order_field = 'necesita_reposicion'
    
    def activo_display(self, obj):
        if obj.activo:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Activo</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Inactivo</span>'
            )
    activo_display.short_description = 'Estado'
    activo_display.admin_order_field = 'activo'
    
    def fecha_actualizacion_display(self, obj):
        return obj.fecha_actualizacion.strftime('%d/%m/%Y %H:%M')
    fecha_actualizacion_display.short_description = 'Última Actualización'
    fecha_actualizacion_display.admin_order_field = 'fecha_actualizacion'
    
    # Sobreescribir para agregar información en el form de creación/edición
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si estamos editando un objeto existente
            return self.readonly_fields + ['fecha_actualizacion']
        return self.readonly_fields
    
    # Cambiar el título en el admin
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Puedes personalizar el form aquí si es necesario
        return form

# --- ADMIN CLASS PARA PROVEEDORES ---
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'email', 'insumos_count']
    search_fields = ['nombre', 'email', 'telefono']
    list_per_page = 50
    
    def insumos_count(self, obj):
        count = obj.insumo_set.filter(activo=True).count()
        return format_html('<span class="badge">{}</span>', count)
    insumos_count.short_description = 'Insumos Activos'

# --- ADMIN CLASS PARA CATEGORÍAS ---
@admin.register(CategoriaInsumo)
class CategoriaInsumoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'insumos_count', 'descripcion_short']
    search_fields = ['nombre', 'descripcion']
    list_per_page = 50
    
    def insumos_count(self, obj):
        count = obj.insumo_set.filter(activo=True).count()
        return format_html('<span class="badge">{}</span>', count)
    insumos_count.short_description = 'Insumos Activos'
    
    def descripcion_short(self, obj):
        if obj.descripcion and len(obj.descripcion) > 50:
            return f"{obj.descripcion[:50]}..."
        return obj.descripcion or "-"
    descripcion_short.short_description = 'Descripción'

# --- ADMIN CLASS PARA UNIDADES DE MEDIDA ---
@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'abreviatura', 'es_unidad_base', 'insumos_count']
    search_fields = ['nombre', 'abreviatura']
    list_filter = ['es_unidad_base']
    list_per_page = 50
    
    def insumos_count(self, obj):
        count = obj.insumo_set.filter(activo=True).count()
        return format_html('<span class="badge">{}</span>', count)
    insumos_count.short_description = 'Insumos Activos'

# --- ADMIN CLASS PARA PÉRDIDAS ---
@admin.register(Perdida)
class PerdidaAdmin(admin.ModelAdmin):
    list_display = ['insumo', 'cantidad_display', 'motivo_display', 'fecha', 'observaciones_short']
    list_filter = ['motivo', 'fecha', 'insumo']
    search_fields = ['insumo__nombre', 'observaciones']
    date_hierarchy = 'fecha'
    list_per_page = 50
    
    fields = ['insumo', 'cantidad', 'motivo', 'observaciones', 'fecha']
    
    def cantidad_display(self, obj):
        return format_html(
            '<strong>{:.3f} {}</strong>',
            obj.cantidad,
            obj.insumo.unidad_medida.abreviatura
        )
    cantidad_display.short_description = 'Cantidad'
    
    def motivo_display(self, obj):
        colors = {
            'deterioro': 'orange',
            'vencimiento': 'red',
            'rotura': 'brown',
            'error': 'purple',
            'uso_interno': 'blue',
            'otro': 'gray'
        }
        color = colors.get(obj.motivo, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_motivo_display()
        )
    motivo_display.short_description = 'Motivo'
    
    def observaciones_short(self, obj):
        if obj.observaciones and len(obj.observaciones) > 30:
            return f"{obj.observaciones[:30]}..."
        return obj.observaciones or "-"
    observaciones_short.short_description = 'Observaciones'

# --- ADMIN CLASS PARA HISTORIAL DE STOCK ---
@admin.register(HistorialStock)
class HistorialStockAdmin(admin.ModelAdmin):
    list_display = ['insumo', 'tipo_movimiento_display', 'cantidad_display', 'fecha', 'descripcion_short']
    list_filter = ['tipo_movimiento', 'fecha', 'insumo']
    search_fields = ['insumo__nombre', 'descripcion']
    date_hierarchy = 'fecha'
    list_per_page = 50
    readonly_fields = ['insumo', 'tipo_movimiento', 'cantidad', 'unidad_medida', 'fecha', 'descripcion']
    
    def tipo_movimiento_display(self, obj):
        colors = {
            'RECETA': 'blue',
            'INGREDIENTE_EXTRA': 'green',
            'AJUSTE': 'orange',
            'COMPRA': 'purple',
            'PERDIDA': 'red'
        }
        color = colors.get(obj.tipo_movimiento, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_tipo_movimiento_display()
        )
    tipo_movimiento_display.short_description = 'Tipo de Movimiento'
    
    def cantidad_display(self, obj):
        color = 'red' if obj.cantidad < 0 else 'green'
        sign = '' if obj.cantidad < 0 else '+'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}{:.3f} {}</span>',
            color,
            sign,
            obj.cantidad,
            obj.unidad_medida.abreviatura
        )
    cantidad_display.short_description = 'Cantidad'
    
    def descripcion_short(self, obj):
        if obj.descripcion and len(obj.descripcion) > 30:
            return f"{obj.descripcion[:30]}..."
        return obj.descripcion or "-"
    descripcion_short.short_description = 'Descripción'
    
    def has_add_permission(self, request):
        return False  # No permitir agregar manualmente

# --- CONFIGURACIÓN DEL SITIO ADMIN ---
# Cambiar título del admin
admin.site.site_header = "Sistema de Gestión de Insumos"
admin.site.site_title = "Admin Insumos"
admin.site.index_title = "Panel de Administración"