from django.db.models import F
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView  # ✅ Agregar esta importación
from .models import Insumo, UnidadMedida, CategoriaInsumo, Proveedor
from .serializers import InsumoSerializer, UnidadMedidaSerializer, CategoriaInsumoSerializer, ProveedorSerializer
from django.http import HttpResponse
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Q
from django.db import models
from datetime import datetime, timedelta, date  # ✅ Agregar date
from decimal import Decimal
import io

class UnidadMedidaListAPIView(generics.ListAPIView):
    queryset = UnidadMedida.objects.all()
    serializer_class = UnidadMedidaSerializer

class UnidadMedidaDetailAPIView(generics.RetrieveAPIView):
    queryset = UnidadMedida.objects.all()
    serializer_class = UnidadMedidaSerializer

class InsumoListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Insumo.objects.filter(activo=True)
    serializer_class = InsumoSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'insumos': serializer.data,
            'total': queryset.count(),
            'necesitan_reposicion': queryset.filter(stock_actual__lt=F('stock_minimo')).count()
        })

class InsumoCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer

    def create(self, request, *args, **kwargs):
        # Validar si ya existe una categoría con el mismo nombre
        nombre = request.data.get('nombre', '').strip()
        if Insumo.objects.filter(nombre__iexact=nombre).exists():
            return Response(
                {
                    'error': 'Ya existe un insumo con este nombre'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'Insumo creado exitosamente',
                'insumo': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class InsumoRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    lookup_field = 'id'

class InsumoUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(
            {
                'message': 'Insumo actualizado exitosamente',
                'insumo': serializer.data
            }
        )

class InsumoPartialUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    lookup_field = 'id'

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Permite actualización parcial sin requerir todos los campos
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(
            {
                'message': 'Insumo actualizado parcialmente',
                'insumo': serializer.data
            }
        )

class InsumoDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Soft delete: marcar como inactivo en lugar de eliminar
        instance.activo = False
        instance.save()
        
        return Response(
            {
                'message': 'Insumo eliminado exitosamente',
                'insumo_id': instance.id
            },
            status=status.HTTP_200_OK
        )
    
class CategoriaInsumoCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CategoriaInsumo.objects.all()
    serializer_class = CategoriaInsumoSerializer

    def create(self, request, *args, **kwargs):
        # Validar si ya existe una categoría con el mismo nombre
        nombre = request.data.get('nombre', '').strip()
        if CategoriaInsumo.objects.filter(nombre__iexact=nombre).exists():
            return Response(
                {
                    'error': 'Ya existe una categoría con este nombre'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'Categoría creada exitosamente',
                'categoria': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
class UnidadMedidaCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = UnidadMedida.objects.all()
    serializer_class = UnidadMedidaSerializer

    def create(self, request, *args, **kwargs):
        # Validar si ya existe una unidadMedida con el mismo nombre
        nombre = request.data.get('nombre', '').strip()
        if UnidadMedida.objects.filter(nombre__iexact=nombre).exists():
            return Response(
                {
                    'error': 'Ya existe una unidad con este nombre'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'Unidad de Medida creada exitosamente',
                'categoria': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class InsumoHardDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id = instance.id
        self.perform_destroy(instance)
        
        return Response(
            {
                'message': 'Insumo eliminado permanentemente',
                'insumo_id': instance_id
            },
            status=status.HTTP_204_NO_CONTENT
        )

# Vistas para Categorías
class CategoriaInsumoListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CategoriaInsumo.objects.all()
    serializer_class = CategoriaInsumoSerializer

# Vistas para Proveedores
class ProveedorListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class ProveedorCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

    def create(self, request, *args, **kwargs):
        # Validar si ya existe un proveedor con el mismo nombre
        nombre = request.data.get('nombre', '').strip()
        if Proveedor.objects.filter(nombre__iexact=nombre).exists():
            return Response(
                {
                    'error': 'Ya existe un proveedor con este nombre'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'Proveedor creado exitosamente',
                'proveedor': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
class ReporteInsumosAPIView(APIView):
    """
    Vista para generar reportes de insumos con cálculo de stock usado
    """
    def get(self, request):
        try:
            # Obtener parámetros de filtro
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            proveedor_id = request.GET.get('proveedor_id')
            
            # Filtrar insumos activos
            insumos = Insumo.objects.filter(activo=True)
            
            # Aplicar filtro por proveedor
            if proveedor_id:
                insumos = insumos.filter(proveedor_id=proveedor_id)
            
            reporte_data = []
            for insumo in insumos:
                # Calcular stock usado desde recetas
                stock_usado_recetas = self.calcular_stock_usado_recetas(insumo, fecha_inicio, fecha_fin)
                
                # Calcular stock usado desde ingredientes extra
                stock_usado_ingredientes_extra = self.calcular_stock_usado_ingredientes_extra(insumo, fecha_inicio, fecha_fin)
                
                # Stock total usado
                stock_usado_total = stock_usado_recetas + stock_usado_ingredientes_extra
                
                reporte_data.append({
                    'id': insumo.id,
                    'nombre': insumo.nombre,
                    'categoria': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                    'stock_usado': float(stock_usado_total),
                    'stock_actual': float(insumo.stock_actual),
                    'stock_minimo': float(insumo.stock_minimo),
                    'unidad_medida': {
                        'abreviatura': insumo.unidad_medida.abreviatura
                    },
                    'necesita_reposicion': insumo.necesita_reposicion,
                    'proveedor': {
                        'id': insumo.proveedor.id if insumo.proveedor else None,
                        'nombre': insumo.proveedor.nombre if insumo.proveedor else 'Sin proveedor'
                    } if insumo.proveedor else None
                })
            
            return Response(reporte_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al generar reporte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def calcular_stock_usado_recetas(self, insumo, fecha_inicio, fecha_fin):
        """
        Calcula el stock usado por recetas para un insumo específico
        """
        try:
            from recetas.models import RecetaInsumo, Receta
            
            # Obtener todas las recetas que usan este insumo
            recetas_insumos = RecetaInsumo.objects.filter(insumo=insumo)
            
            stock_usado_total = Decimal('0.0')
            
            for receta_insumo in recetas_insumos:
                receta = receta_insumo.receta
                
                # Si hay filtro de fecha, considerar solo las veces hechas en ese período
                if fecha_inicio and fecha_fin:
                    # Convertir fechas
                    fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                    fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                    
                    # En una implementación real, necesitarías un modelo de historial
                    # que registre cuándo se preparó cada receta
                    # Por ahora, usamos un cálculo proporcional basado en veces_hecha
                    veces_en_periodo = self.estimar_veces_en_periodo(receta, fecha_inicio_dt, fecha_fin_dt)
                else:
                    # Sin filtro de fecha, usar todas las veces hechas
                    veces_en_periodo = receta.veces_hecha
                
                # Calcular cantidad usada por receta
                cantidad_por_receta = receta_insumo.get_cantidad_en_unidad_insumo()
                stock_usado = cantidad_por_receta * Decimal(str(veces_en_periodo))
                stock_usado_total += stock_usado
            
            return stock_usado_total
            
        except Exception as e:
            print(f"Error calculando stock usado en recetas: {e}")
            return Decimal('0.0')
    
    def calcular_stock_usado_ingredientes_extra(self, insumo, fecha_inicio, fecha_fin):
        """
        Calcula el stock usado por ingredientes extra para un insumo específico
        """
        try:
            from pedidos.models import IngredientesExtra, Pedido
            
            # Filtrar ingredientes extra por insumo
            ingredientes_query = IngredientesExtra.objects.filter(insumo=insumo)
            
            # Aplicar filtro de fecha si existe
            if fecha_inicio and fecha_fin:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                
                # Filtrar por pedidos en el rango de fechas
                ingredientes_query = ingredientes_query.filter(
                    detalle__pedido__fecha_entrega__range=[fecha_inicio_dt, fecha_fin_dt]
                )
            
            # Sumar todas las cantidades de ingredientes extra
            stock_usado_total = Decimal('0.0')
            for ingrediente in ingredientes_query:
                # Convertir a la unidad del insumo si es necesario
                if ingrediente.unidad_medida != insumo.unidad_medida:
                    try:
                        # Usar el método de conversión del modelo RecetaInsumo
                        cantidad_convertida = self.convertir_cantidad(
                            ingrediente.cantidad,
                            ingrediente.unidad_medida.abreviatura,
                            insumo.unidad_medida.abreviatura
                        )
                        stock_usado_total += cantidad_convertida
                    except Exception as conv_error:
                        print(f"Error en conversión: {conv_error}")
                        # Si falla la conversión, usar la cantidad original
                        stock_usado_total += ingrediente.cantidad
                else:
                    stock_usado_total += ingrediente.cantidad
            
            return stock_usado_total
            
        except Exception as e:
            print(f"Error calculando stock usado en ingredientes extra: {e}")
            return Decimal('0.0')
    
    def convertir_cantidad(self, cantidad, unidad_origen, unidad_destino):
        """
        Método auxiliar para convertir cantidades entre unidades
        """
        try:
            # Importar el módulo de conversiones
            from insumos.conversiones import convertir_unidad
            
            cantidad_decimal = Decimal(str(cantidad))
            return convertir_unidad(cantidad_decimal, unidad_origen, unidad_destino)
            
        except Exception as e:
            print(f"Error en conversión manual: {e}")
            # Fallback: conversiones básicas
            conversiones = {
                ('kg', 'g'): lambda x: x * 1000,
                ('g', 'kg'): lambda x: x / 1000,
                ('l', 'ml'): lambda x: x * 1000,
                ('ml', 'l'): lambda x: x / 1000,
            }
            
            conversion_key = (unidad_origen.lower(), unidad_destino.lower())
            if conversion_key in conversiones:
                return conversiones[conversion_key](cantidad_decimal)
            
            # Si no hay conversión disponible, devolver la cantidad original
            return cantidad_decimal
    
    def estimar_veces_en_periodo(self, receta, fecha_inicio, fecha_fin):
        """
        Estima cuántas veces se preparó una receta en un período específico
        En una implementación real, esto vendría de un modelo de historial
        """
        # Por ahora, usamos una estimación simple basada en la fecha de creación
        # y las veces hechas totales
        if receta.creado_en.date() >= fecha_inicio and receta.creado_en.date() <= fecha_fin:
            return receta.veces_hecha
        else:
            # Estimación: asumimos que se distribuye uniformemente en el tiempo
            dias_total = (date.today() - receta.creado_en.date()).days
            if dias_total <= 0:
                return receta.veces_hecha
            
            dias_periodo = (fecha_fin - fecha_inicio).days
            proporcion = dias_periodo / dias_total
            return int(receta.veces_hecha * proporcion)


class GenerarPDFReporteAPIView(APIView):
    """
    Vista para generar PDF del reporte de insumos
    """
    def get(self, request):
        try:
            # Obtener parámetros de filtro
            fecha_inicio = request.GET.get('fecha_inicio', '')
            fecha_fin = request.GET.get('fecha_fin', '')
            proveedor_id = request.GET.get('proveedor_id', '')
            
            # Obtener datos del reporte usando la misma lógica que ReporteInsumosAPIView
            reporte_view = ReporteInsumosAPIView()
            response = reporte_view.get(request)
            
            if response.status_code != 200:
                return response
            
            reporte_data = response.data
            
            # Crear el PDF
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                textColor=colors.HexColor('#7b5a50')
            )
            
            # Título
            title_text = "Reporte de Insumos - Alma Pastelería"
            elements.append(Paragraph(title_text, title_style))
            
            # Información de filtros
            filtros_text = f"Fecha: {fecha_inicio} a {fecha_fin}" if fecha_inicio else "Todos los insumos"
            if proveedor_id:
                try:
                    proveedor = Proveedor.objects.get(id=proveedor_id)
                    filtros_text += f" | Proveedor: {proveedor.nombre}"
                except Proveedor.DoesNotExist:
                    pass
            
            elements.append(Paragraph(filtros_text, styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Preparar datos de la tabla
            table_data = [['Insumo', 'Stock Usado', 'Stock Actual', 'Stock Mínimo', 'Reponer?', 'Proveedor']]
            
            for item in reporte_data:
                table_data.append([
                    f"{item['nombre']}\n({item['categoria']})",
                    f"{item['stock_usado']:.3f} {item['unidad_medida']['abreviatura']}",
                    f"{item['stock_actual']:.3f} {item['unidad_medida']['abreviatura']}",
                    f"{item['stock_minimo']:.3f} {item['unidad_medida']['abreviatura']}",
                    "SÍ" if item['necesita_reposicion'] else "NO",
                    item['proveedor']['nombre'] if item['proveedor'] else "Sin proveedor"
                ])
            
            # Crear tabla
            table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 0.8*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7b5a50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Agregar resumen
            elementos_reponer = sum(1 for item in reporte_data if item['necesita_reposicion'])
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(f"Total de insumos: {len(reporte_data)}", styles['Normal']))
            elements.append(Paragraph(f"Necesitan reposición: {elementos_reponer}", styles['Normal']))
            
            # Generar PDF
            doc.build(elements)
            buffer.seek(0)
            
            # Crear respuesta
            response = HttpResponse(buffer, content_type='application/pdf')
            filename = f"reporte_insumos_{date.today().strftime('%Y-%m-%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error al generar PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )