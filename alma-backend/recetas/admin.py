from django.contrib import admin
from .models import Receta, RecetaInsumo
# Register your models here.

class RecetaInsumoInline(admin.TabularInline):
    model = RecetaInsumo
    extra = 1
    fields = ['insumo', 'cantidad', 'unidad_medida']

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    inlines = [RecetaInsumoInline]