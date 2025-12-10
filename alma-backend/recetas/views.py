from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from decimal import Decimal
from django.utils import timezone
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from datetime import datetime
import pytz

# Importar los modelos correctamente
from .models import Receta, RecetaInsumo, HistorialReceta
from .serializers import RecetaSerializer, RecetaInsumoSerializer, RecetaInsumoCreateSerializer
from insumos.models import Insumo
from insumos.conversiones import convertir_unidad

# FUNCION PARA MOSTRAR FECHAS REALES

def convertir_a_hora_local(fecha_utc):
    """Convierte fecha UTC a hora Argentina"""
    tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
    if fecha_utc and fecha_utc.tzinfo is None:
        fecha_utc = pytz.UTC.localize(fecha_utc)
    return fecha_utc.astimezone(tz_argentina)

class RecetaListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Receta.objects.all().order_by('-creado_en')
    serializer_class = RecetaSerializer

    def perform_create(self, serializer):
        print("Datos recibidos:", self.request.data)
        instance = serializer.save()
        
        # Calcular y guardar costos inmediatamente
        instance.costo_total = instance.calcular_costo_total()
        if instance.rinde and instance.rinde > 0:
            instance.costo_unitario = instance.costo_total / Decimal(str(instance.rinde))
        else:
            instance.costo_unitario = Decimal('0.00')
        
        instance.save()  # Esto activará el método save() que actualizará los costos
        
        # Recargar para obtener datos actualizados
        instance.refresh_from_db()
    
    def get_queryset(self):
        try:
            # ✅ VERIFICAR CIERRE AUTOMÁTICO DE FORMA SEGURA
            from recetas.models import Receta
            Receta.verificar_cierre_automatico()
            
        except Exception as e:
            print(f"❌ Error en verificación automática: {e}")
            # Continuar sin bloquear la respuesta
        
        queryset = Receta.objects.prefetch_related('insumos__insumo', 'insumos__unidad_medida').order_by('-creado_en')
        
        # Verificación individual para cada receta
        for receta in queryset:
            try:
                receta.verificar_reinicio_diario()
            except Exception as e:
                print(f"❌ Error en verificar_reinicio_diario para {receta.nombre}: {e}")
                continue
            
        return queryset

class RecetaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Receta.objects.all()
    serializer_class = RecetaSerializer
    permission_classes = [permissions.IsAuthenticated]


class RecetaInsumoListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        receta_id = self.kwargs['receta_id']
        return RecetaInsumo.objects.filter(receta_id=receta_id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecetaInsumoCreateSerializer
        return RecetaInsumoSerializer

    def perform_create(self, serializer):
        receta_id = self.kwargs['receta_id']
        serializer.save(receta_id=receta_id)

class RecetaInsumoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecetaInsumoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        receta_id = self.kwargs['receta_id']
        return RecetaInsumo.objects.filter(receta_id=receta_id)

    def update(self, request, *args, **kwargs):
        print("🔧 Actualizando insumo de receta")
        print("Datos recibidos:", request.data)
        print("Receta ID:", kwargs.get('receta_id'))
        print("Insumo ID:", kwargs.get('pk'))
        
        response = super().update(request, *args, **kwargs)
        print("Respuesta:", response.data)
        return response
    
class RecetaInsumoPartialUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, receta_id, pk):
        try:
            receta_insumo = RecetaInsumo.objects.get(receta_id=receta_id, pk=pk)
            
            serializer = RecetaInsumoCreateSerializer(
                receta_insumo, 
                data=request.data, 
                partial=True  # Permitir actualización parcial
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except RecetaInsumo.DoesNotExist:
            return Response({'error': 'Insumo de receta no encontrado'}, 
                          status=status.HTTP_404_NOT_FOUND)


# -------------------------
# 🔹 Incrementar Receta
# -------------------------
class IncrementarRecetaView(APIView):
    def post(self, request, pk):
        try:
            with transaction.atomic():
                receta = Receta.objects.get(pk=pk)
                detalles = RecetaInsumo.objects.filter(receta=receta).select_related(
                    'insumo', 'insumo__unidad_medida', 'unidad_medida'
                )

                # Verificar stock antes de incrementar
                insuficientes = []
                for detalle in detalles:
                    try:
                        cantidad_necesaria = detalle.get_cantidad_en_unidad_insumo()
                        print(f"   - Cantidad convertida: {cantidad_necesaria} {detalle.insumo.unidad_medida.abreviatura}")
                    except Exception as e:
                        print(f"❌ Error en conversión: {e}")
                        # Fallback a cantidad original
                        cantidad_necesaria = detalle.cantidad
                    
                    if not isinstance(cantidad_necesaria, Decimal):
                        cantidad_necesaria = Decimal(str(cantidad_necesaria))

                    stock_actual = detalle.insumo.stock_actual
                    if not isinstance(stock_actual, Decimal):
                        stock_actual = Decimal(str(stock_actual))

                    print(f"   - Stock actual: {stock_actual} {detalle.insumo.unidad_medida.abreviatura}")
                    print(f"   - ¿Suficiente? {stock_actual >= cantidad_necesaria}")

                    if stock_actual < cantidad_necesaria:
                        insuficientes.append({
                            'nombre': detalle.insumo.nombre,
                            'disponible': float(stock_actual),
                            'necesario': float(cantidad_necesaria),
                            'unidad': detalle.insumo.unidad_medida.abreviatura
                        })

                if insuficientes:
                    return Response({
                        'error': 'Stock insuficiente para preparar la receta',
                        'insuficientes': insuficientes,
                        'receta_nombre': receta.nombre
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Reducir stock usando la cantidad convertida
                for detalle in detalles:
                    # Obtener la cantidad convertida
                    try:
                        cantidad_necesaria = detalle.get_cantidad_en_unidad_insumo()
                    except Exception as e:
                        print(f"⚠️ Error en conversión durante descuento: {e}")
                        cantidad_necesaria = detalle.cantidad
                    
                    if not isinstance(cantidad_necesaria, Decimal):
                        cantidad_necesaria = Decimal(str(cantidad_necesaria))
                    
                    if not isinstance(detalle.insumo.stock_actual, Decimal):
                        detalle.insumo.stock_actual = Decimal(str(detalle.insumo.stock_actual))
                    
                    print(f"💰 Descontando: {cantidad_necesaria} {detalle.insumo.unidad_medida.abreviatura} de {detalle.insumo.nombre}")
                    
                    detalle.insumo.stock_actual -= cantidad_necesaria
                    detalle.insumo.save()

                # ✅ CAMBIO IMPORTANTE: Usar el método del modelo que crea el historial
                receta.incrementar_contador_diario()

                return Response({
                    'nuevo_contador': receta.veces_hecha,
                    'veces_hecha': receta.veces_hecha,
                    'veces_hecha_hoy': receta.veces_hecha_hoy,
                    'stock_actualizado': True,
                    'mensaje': f'Receta "{receta.nombre}" preparada exitosamente'
                }, status=status.HTTP_200_OK)

        except Receta.DoesNotExist:
            return Response({'error': 'Receta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Error interno del servidor: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# -------------------------
# 🔹 Decrementar Receta
# -------------------------
class DecrementarRecetaView(APIView):
    def post(self, request, pk):
        try:
            with transaction.atomic():
                receta = Receta.objects.get(pk=pk)
                
                # ✅ VERIFICAR AMBOS CONTADORES
                if receta.veces_hecha <= 0 or receta.veces_hecha_hoy <= 0:
                    return Response({
                        'error': 'El contador ya está en cero',
                        'receta_nombre': receta.nombre
                    }, status=status.HTTP_400_BAD_REQUEST)

                detalles = RecetaInsumo.objects.filter(receta=receta)

                insumos_devueltos = []
                for detalle in detalles:
                    insumo = detalle.insumo
                    cantidad_devolver = detalle.get_cantidad_en_unidad_insumo()
                    if not isinstance(cantidad_devolver, Decimal):
                        cantidad_devolver = Decimal(str(cantidad_devolver))

                    # Asegurar que stock_actual sea Decimal
                    if not isinstance(insumo.stock_actual, Decimal):
                        insumo.stock_actual = Decimal(str(insumo.stock_actual))
                    
                    insumo.stock_actual += cantidad_devolver
                    insumo.save()

                    insumos_devueltos.append({
                        'nombre': insumo.nombre,
                        'cantidad': float(cantidad_devolver),
                        'unidad': insumo.unidad_medida.abreviatura
                    })

                # ✅ CAMBIO IMPORTANTE: Usar el método del modelo que maneja el historial
                receta.decrementar_contador_diario()

                return Response({
                    'nuevo_contador': receta.veces_hecha,
                    'veces_hecha_hoy': receta.veces_hecha_hoy,
                    'stock_actualizado': True,
                    'mensaje': f'Se ha revertido la preparación de "{receta.nombre}"',
                    'insumos_devueltos': insumos_devueltos
                }, status=status.HTTP_200_OK)

        except Receta.DoesNotExist:
            return Response({'error': 'Receta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Error interno del servidor: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RecetasHechasHoyView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            # Obtener fecha de hoy
            fecha_hoy = timezone.now().date()
            
            # Filtrar recetas que se han preparado hoy (veces_hecha_hoy > 0)
            recetas_hoy = Receta.objects.filter(
                veces_hecha_hoy__gt=0
            ).order_by('-id')
            
            # Preparar datos para la respuesta
            recetas_data = []
            for receta in recetas_hoy:
                recetas_data.append({
                    'id': receta.id,
                    'nombre': receta.nombre,
                    'cantidad': receta.veces_hecha_hoy,  # Cuántas veces se preparó hoy
                    'fecha': fecha_hoy.isoformat(),
                    'hora': 'Todo el día',  # O puedes usar la hora actual
                    'estado': 'Completado',
                    'empleado': 'Sistema',  # O puedes obtener el usuario del request
                    'rinde': receta.rinde,
                    'unidad_rinde': receta.unidad_rinde,
                    'costo_total': float(receta.costo_total) if receta.costo_total else 0,
                    'precio_venta': float(receta.precio_venta) if receta.precio_venta else 0
                })
            
            return Response({
                'fecha': fecha_hoy.isoformat(),
                'total_recetas': len(recetas_data),
                'recetas': recetas_data
            })
            
        except Exception as e:
            print(f"❌ Error en RecetasHechasHoyView: {str(e)}")
            return Response({
                'error': f'Error interno del servidor: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RecetasPorFechaView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            # Obtener fechas del query parameter
            fecha_inicio_str = request.GET.get('fecha_inicio')
            fecha_fin_str = request.GET.get('fecha_fin')
            
            tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
            
            # Usar el historial en lugar de las recetas directamente
            historial_query = HistorialReceta.objects.select_related('receta')
            
            # Bandera para indicar si hay filtro por fecha
            tiene_filtro_fecha = False
            
            # Aplicar filtro por fecha si se proporciona
            if fecha_inicio_str and fecha_fin_str:
                tiene_filtro_fecha = True
                # Convertir a fecha Argentina
                fecha_inicio_arg = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                fecha_fin_arg = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
                
                # Convertir a UTC para la consulta
                fecha_inicio_utc = tz_argentina.localize(
                    datetime.combine(fecha_inicio_arg, datetime.min.time())
                ).astimezone(pytz.UTC)
                
                fecha_fin_utc = tz_argentina.localize(
                    datetime.combine(fecha_fin_arg, datetime.min.time())
                ).replace(hour=23, minute=59, second=59).astimezone(pytz.UTC)
                
                # Filtrar por fecha de preparación en UTC
                historial_query = historial_query.filter(
                    fecha_preparacion__range=[fecha_inicio_utc, fecha_fin_utc]
                )
                
            elif fecha_inicio_str:
                # Si solo hay fecha inicio, buscar solo ese día
                tiene_filtro_fecha = True
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                
                fecha_inicio_utc = tz_argentina.localize(
                    datetime.combine(fecha_inicio, datetime.min.time())
                ).astimezone(pytz.UTC)
                
                fecha_fin_utc = tz_argentina.localize(
                    datetime.combine(fecha_inicio, datetime.min.time())
                ).replace(hour=23, minute=59, second=59).astimezone(pytz.UTC)
                
                historial_query = historial_query.filter(
                    fecha_preparacion__range=[fecha_inicio_utc, fecha_fin_utc]
                )
            
            # 🔹 CAMBIO: Si NO hay filtro de fecha, mostrar TODAS las preparaciones del historial
            # No aplicamos ningún filtro cuando no hay fechas especificadas
            
            print(f"🔍 Consultando historial. Tiene filtro fecha: {tiene_filtro_fecha}")
            print(f"🔍 Total registros en historial: {historial_query.count()}")
            
            # 🔹 AGREGAR: Agrupar por receta Y por fecha
            from django.db.models import Sum
            from django.db.models.functions import TruncDate
            
            # Agrupar por receta y fecha de preparación (en hora Argentina)
            recetas_agrupadas = historial_query.annotate(
                fecha_preparacion_arg=TruncDate('fecha_preparacion', tzinfo=tz_argentina)
            ).values(
                'receta_id',
                'receta__nombre',
                'receta__rinde',
                'receta__unidad_rinde',
                'fecha_preparacion_arg',
                'costo_total_historico',
                'precio_venta_historico'
            ).annotate(
                total_preparaciones=Sum('cantidad_preparada')
            ).order_by('-fecha_preparacion_arg', 'receta__nombre')
            
            print(f"🔍 Recetas agrupadas encontradas: {recetas_agrupadas.count()}")
            
            # Preparar datos para la respuesta
            recetas_data = []
            for grupo in recetas_agrupadas:
                # Formatear fecha en formato Argentina
                fecha_prep = grupo['fecha_preparacion_arg']
                if fecha_prep:
                    fecha_arg_str = fecha_prep.strftime('%d/%m/%Y')
                else:
                    fecha_arg_str = "Sin fecha"
                
                # 🔹 USAR VALORES HISTÓRICOS
                costo_por_preparacion = grupo['costo_total_historico'] or Decimal('0')
                precio_venta_historico = grupo['precio_venta_historico'] or Decimal('0')
                
                # Calcular costo total para esa cantidad de preparaciones
                costo_total_dia = costo_por_preparacion * Decimal(str(grupo['total_preparaciones']))
                
                recetas_data.append({
                    'id': grupo['receta_id'],
                    'nombre': grupo['receta__nombre'],
                    'cantidad': grupo['total_preparaciones'],
                    'rinde': grupo['receta__rinde'],
                    'unidad_rinde': grupo['receta__unidad_rinde'],
                    'costo_total': float(costo_total_dia),
                    'precio_venta': float(precio_venta_historico) if precio_venta_historico else 0,
                    'fecha_preparacion': fecha_arg_str,  # ✅ Fecha específica de ese día
                    'fecha_preparacion_original': fecha_prep.isoformat() if fecha_prep else None
                })
            
            return Response({
                'fecha_inicio': fecha_inicio_str,
                'fecha_fin': fecha_fin_str,
                'total_preparaciones': sum(g['total_preparaciones'] for g in recetas_agrupadas),
                'total_dias': len(set(g['fecha_preparacion_arg'] for g in recetas_agrupadas if g['fecha_preparacion_arg'])),
                'recetas': recetas_data
            })
            
        except Exception as e:
            print(f"❌ Error en RecetasPorFechaView: {str(e)}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return Response({
                'error': f'Error interno del servidor: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GenerarPDFRecetasView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            # Obtener parámetros de filtro
            fecha_inicio_str = request.GET.get('fecha_inicio')
            fecha_fin_str = request.GET.get('fecha_fin')
            
            # Crear buffer para el PDF
            buffer = io.BytesIO()
            
            # Crear el documento PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Lista de elementos para el PDF
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1,
                textColor=colors.HexColor('#2c3e50')
            )
            
            # Título
            title_text = "Reporte de Recetas Preparadas"
            elements.append(Paragraph(title_text, title_style))
            
            # Información de fechas
            if fecha_inicio_str and fecha_fin_str:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
                fecha_text = f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
            else:
                fecha_text = "Período: Todas las fechas"
            
            date_style = ParagraphStyle(
                'CustomDate',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=20,
                alignment=1,
                textColor=colors.HexColor('#7f8c8d')
            )
            elements.append(Paragraph(fecha_text, date_style))
            
            # Obtener datos usando la misma lógica que RecetasPorFechaView
            tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
            historial_query = HistorialReceta.objects.select_related('receta')
            
            if fecha_inicio_str and fecha_fin_str:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
                
                # Convertir a UTC para la consulta
                fecha_inicio_utc = tz_argentina.localize(
                    datetime.combine(fecha_inicio, datetime.min.time())
                ).astimezone(pytz.UTC)
                
                fecha_fin_utc = tz_argentina.localize(
                    datetime.combine(fecha_fin, datetime.min.time())
                ).replace(hour=23, minute=59, second=59).astimezone(pytz.UTC)
                
                historial_query = historial_query.filter(
                    fecha_preparacion__range=[fecha_inicio_utc, fecha_fin_utc]
                )
            
            # 🔹 Agrupar por receta Y fecha
            from django.db.models import Sum
            from django.db.models.functions import TruncDate
            
            recetas_agrupadas = historial_query.annotate(
                fecha_preparacion_arg=TruncDate('fecha_preparacion', tzinfo=tz_argentina)
            ).values(
                'receta_id',
                'receta__nombre',
                'fecha_preparacion_arg',
                # 🔹 USAR VALORES HISTÓRICOS
                'costo_total_historico',
                'precio_venta_historico'
            ).annotate(
                total_preparaciones=Sum('cantidad_preparada')
            ).order_by('-fecha_preparacion_arg', 'receta__nombre')
            
            # Preparar datos para la tabla
            if recetas_agrupadas:
                # Encabezados de la tabla
                data = [['Fecha', 'Receta', 'Preparaciones', 'Costo Total', 'Precio Venta']]
                
                for grupo in recetas_agrupadas:
                    # Formatear datos
                    fecha = grupo['fecha_preparacion_arg'].strftime('%d/%m/%Y') if grupo['fecha_preparacion_arg'] else "N/A"
                    nombre = grupo['receta__nombre']
                    preparaciones = str(grupo['total_preparaciones'])
                    
                    # 🔹 USAR VALORES HISTÓRICOS
                    costo_por_preparacion = grupo['costo_total_historico'] or Decimal('0')
                    precio_venta_historico = grupo['precio_venta_historico'] or Decimal('0')
                    
                    costo_total_dia = costo_por_preparacion * Decimal(str(grupo['total_preparaciones']))
                    
                    costo_total = f"${costo_total_dia:.2f}"
                    precio_venta = f"${precio_venta_historico:.2f}" if precio_venta_historico else "$0.00"
                    
                    data.append([fecha, nombre, preparaciones, costo_total, precio_venta])
                
                # Crear tabla
                table = Table(data, colWidths=[1.2*inch, 2.5*inch, 1*inch, 1*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
                ]))
                
                elements.append(table)
                
                # Agregar resumen
                elements.append(Spacer(1, 20))
                
                total_dias = len(set(g['fecha_preparacion_arg'] for g in recetas_agrupadas))
                total_preparaciones = sum(g['total_preparaciones'] for g in recetas_agrupadas)
                total_recetas_diferentes = len(set(g['receta_id'] for g in recetas_agrupadas))
                
                summary_style = ParagraphStyle(
                    'CustomSummary',
                    parent=styles['Normal'],
                    fontSize=11,
                    spaceAfter=10,
                    textColor=colors.HexColor('#2c3e50')
                )
                
                elements.append(Paragraph(f"Total de días con preparaciones: {total_dias}", summary_style))
                elements.append(Paragraph(f"Total de recetas diferentes: {total_recetas_diferentes}", summary_style))
                elements.append(Paragraph(f"Total de preparaciones: {total_preparaciones}", summary_style))
                
            else:
                # No hay datos
                no_data_style = ParagraphStyle(
                    'CustomNoData',
                    parent=styles['Normal'],
                    fontSize=12,
                    spaceAfter=20,
                    alignment=1,
                    textColor=colors.HexColor('#e74c3c')
                )
                elements.append(Paragraph("No hay preparaciones en el período seleccionado", no_data_style))
            
            # Pie de página
            elements.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'CustomFooter',
                parent=styles['Normal'],
                fontSize=9,
                alignment=1,
                textColor=colors.HexColor('#95a5a6')
            )
            generated_date = datetime.now().strftime('%d/%m/%Y %H:%M')
            elements.append(Paragraph(f"Generado el: {generated_date}", footer_style))
            elements.append(Paragraph("Alma Pastelería - Sistema de Gestión", footer_style))
            
            # Construir PDF
            doc.build(elements)
            
            # Preparar respuesta
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            
            # Nombre del archivo
            if fecha_inicio_str and fecha_fin_str:
                filename = f"recetas_{fecha_inicio_str}_a_{fecha_fin_str}.pdf"
            else:
                filename = f"recetas_completas_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            print(f"❌ Error en GenerarPDFRecetasView: {str(e)}")
            return Response({
                'error': f'Error al generar PDF: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# -------------------------
# 🔹 Cierre Diario 
# -------------------------
class CierreDiarioView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            with transaction.atomic():
                # Obtener fecha de ayer (cerrar el día anterior)
                ahora = timezone.now()
                if ahora.hour < 5:  # Antes de las 5 AM, cerrar el día anterior
                    ayer = ahora - timezone.timedelta(days=1)
                    fecha_cierre = ayer.date()
                else:
                    fecha_cierre = ahora.date()
                
                print(f"🔹 Iniciando cierre diario para {fecha_cierre}")
                
                # Obtener todas las recetas con actividad hoy
                recetas_con_actividad = Receta.objects.filter(veces_hecha_hoy__gt=0)
                print(f"🔹 Recetas con actividad: {recetas_con_actividad.count()}")
                
                if not recetas_con_actividad.exists():
                    print("🔹 No hay recetas con actividad para cerrar")
                    return Response({
                        'mensaje': 'No hay recetas preparadas hoy para cerrar',
                        'cierre_realizado': False
                    }, status=status.HTTP_200_OK)
                
                # Realizar cierre diario usando el método del modelo
                recetas_procesadas = []
                total_preparaciones = 0
                
                for receta in recetas_con_actividad:
                    print(f"🔹 Procesando receta: {receta.nombre} - Preparaciones: {receta.veces_hecha_hoy}")
                    
                    # ✅ Usar el método realizar_cierre_diario() que ahora crea el historial
                    if receta.realizar_cierre_diario():
                        recetas_procesadas.append({
                            'id': receta.id,
                            'nombre': receta.nombre,
                            'preparaciones': receta.veces_hecha_hoy  # Valor antes de reiniciar
                        })
                        total_preparaciones += receta.veces_hecha_hoy  # Valor antes de reiniciar
                        print(f"🔹 Receta {receta.nombre} cerrada: {receta.veces_hecha_hoy} preparaciones registradas en historial")
                    else:
                        print(f"🔹 Receta {receta.nombre} ya estaba cerrada")
                
                print(f"🔹 Cierre diario completado. Total: {total_preparaciones} preparaciones registradas")
                
                return Response({
                    'mensaje': f'Cierre diario realizado exitosamente para {fecha_cierre}',
                    'cierre_realizado': True,
                    'fecha_cierre': fecha_cierre.isoformat(),
                    'total_recetas_procesadas': len(recetas_procesadas),
                    'total_preparaciones': total_preparaciones,
                    'recetas_procesadas': recetas_procesadas
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            print(f"❌ Error en CierreDiarioView: {str(e)}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return Response({
                'error': f'Error al realizar el cierre diario: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# -------------------------
# 🔹 Actualizar Costos de Recetas
# -------------------------
class ActualizarCostosRecetasView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Opción 1: Actualizar TODAS las recetas
            recetas = Receta.objects.all()
            recetas_actualizadas = []
            
            for receta in recetas:
                costo_anterior = receta.costo_total
                
                # Forzar recálculo llamando al método del serializer
                from .serializers import RecetaSerializer
                serializer = RecetaSerializer(receta)
                
                # Estos llamados activarán los cálculos dinámicos
                nuevo_costo_total = serializer.get_costo_total(receta)
                nuevo_costo_unitario = serializer.get_costo_unitario(receta)
                
                if costo_anterior != nuevo_costo_total:
                    recetas_actualizadas.append({
                        'id': receta.id,
                        'nombre': receta.nombre,
                        'costo_anterior': float(costo_anterior) if costo_anterior else 0,
                        'costo_nuevo': float(nuevo_costo_total),
                        'diferencia': float(nuevo_costo_total - (costo_anterior or Decimal('0.00')))
                    })
            
            return Response({
                'mensaje': 'Costos actualizados exitosamente',
                'total_recetas': len(recetas),
                'recetas_actualizadas': len(recetas_actualizadas),
                'detalles': recetas_actualizadas
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"❌ Error en ActualizarCostosRecetasView: {str(e)}")
            return Response({
                'error': f'Error al actualizar costos: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 🔹 Opción 2: Endpoint para actualizar una receta específica
class ActualizarCostoRecetaView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            receta = Receta.objects.get(pk=pk)
            costo_anterior = receta.costo_total
            
            # Forzar recálculo
            from .serializers import RecetaSerializer
            serializer = RecetaSerializer(receta)
            
            nuevo_costo_total = serializer.get_costo_total(receta)
            nuevo_costo_unitario = serializer.get_costo_unitario(receta)
            
            return Response({
                'id': receta.id,
                'nombre': receta.nombre,
                'costo_anterior': float(costo_anterior) if costo_anterior else 0,
                'costo_total': float(nuevo_costo_total),
                'costo_unitario': float(nuevo_costo_unitario),
                'actualizado': nuevo_costo_total != costo_anterior
            }, status=status.HTTP_200_OK)
            
        except Receta.DoesNotExist:
            return Response({'error': 'Receta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"❌ Error en ActualizarCostoRecetaView: {str(e)}")
            return Response({
                'error': f'Error al actualizar costo: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)