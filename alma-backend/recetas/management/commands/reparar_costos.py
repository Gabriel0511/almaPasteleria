# En recetas/management/commands/reparar_costos.py
from django.core.management.base import BaseCommand
from recetas.models import Receta, RecetaInsumo
from insumos.models import Insumo
from decimal import Decimal
from django.db import transaction

class Command(BaseCommand):
    help = 'Repara los costos de las recetas asegurando tipos Decimal'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # Paso 1: Asegurar que todos los precios unitarios sean Decimal
            self.stdout.write("Paso 1: Asegurando tipos Decimal en precios unitarios...")
            insumos = Insumo.objects.filter(precio_unitario__isnull=False)
            
            for insumo in insumos:
                try:
                    if not isinstance(insumo.precio_unitario, Decimal):
                        insumo.precio_unitario = Decimal(str(insumo.precio_unitario))
                        insumo.save(update_fields=['precio_unitario'])
                        self.stdout.write(f"  ✓ {insumo.nombre}: convertido a Decimal")
                except Exception as e:
                    self.stdout.write(f"  ✗ Error en {insumo.nombre}: {e}")
            
            # Paso 2: Asegurar que todas las cantidades sean Decimal
            self.stdout.write("\nPaso 2: Asegurando tipos Decimal en cantidades...")
            recetas_insumos = RecetaInsumo.objects.all()
            
            for ri in recetas_insumos:
                try:
                    if not isinstance(ri.cantidad, Decimal):
                        ri.cantidad = Decimal(str(ri.cantidad))
                        ri.save(update_fields=['cantidad'])
                        self.stdout.write(f"  ✓ {ri.insumo.nombre}: cantidad convertida")
                except Exception as e:
                    self.stdout.write(f"  ✗ Error en {ri.insumo.nombre}: {e}")
            
            # Paso 3: Recalcular costos para cada receta
            self.stdout.write("\nPaso 3: Recalculando costos de recetas...")
            recetas = Receta.objects.all()
            
            for receta in recetas:
                try:
                    costo_anterior = receta.costo_total
                    nuevo_costo_total = Decimal('0.00')
                    
                    for insumo_receta in receta.insumos.all():
                        if insumo_receta.insumo and insumo_receta.insumo.precio_unitario:
                            # Calcular costo usando el método del modelo
                            costo_insumo = insumo_receta.calcular_costo()
                            nuevo_costo_total += costo_insumo
                    
                    # Redondear
                    nuevo_costo_total = nuevo_costo_total.quantize(Decimal('0.01'))
                    
                    # Calcular costo unitario
                    if receta.rinde and receta.rinde > 0:
                        nuevo_costo_unitario = (nuevo_costo_total / Decimal(str(receta.rinde))).quantize(Decimal('0.01'))
                    else:
                        nuevo_costo_unitario = Decimal('0.00')
                    
                    # Actualizar
                    receta.costo_total = nuevo_costo_total
                    receta.costo_unitario = nuevo_costo_unitario
                    receta.save(update_fields=['costo_total', 'costo_unitario'])
                    
                    self.stdout.write(
                        f"✓ {receta.nombre}: ${costo_anterior} → ${nuevo_costo_total}"
                    )
                    
                except Exception as e:
                    self.stdout.write(f"✗ Error en {receta.nombre}: {e}")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Proceso de reparación completado"))