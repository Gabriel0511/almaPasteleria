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

# Importar los modelos correctamente
from .models import Receta, RecetaInsumo, HistorialReceta
from .serializers import RecetaSerializer, RecetaInsumoSerializer, RecetaInsumoCreateSerializer
from insumos.models import Insumo
from insumos.conversiones import convertir_unidad


class RecetaListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Receta.objects.all().order_by('-creado_en')
    serializer_class = RecetaSerializer

    def perform_create(self, serializer):
        print("Datos recibidos:", self.request.data)
        instance = serializer.save()
        # Forzar recálculo después de crear
        instance.actualizar_costos()
        instance.refresh_from_db()
    
    def get_queryset(self):
        queryset = Receta.objects.prefetch_related('insumos__insumo', 'insumos__unidad_medida').order_by('-creado_en')
        
        for receta in queryset:
            receta.verificar_reinicio_diario()
            
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
            
            # Usar el historial en lugar de las recetas directamente
            historial_query = HistorialReceta.objects.select_related('receta')
            
            # Aplicar filtro por fecha si se proporciona
            if fecha_inicio_str and fecha_fin_str:
                fecha_inicio = timezone.datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                fecha_fin = timezone.datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
                
                # Validar que las fechas no sean futuras
                hoy = timezone.now().date()
                if fecha_inicio > hoy or fecha_fin > hoy:
                    return Response({
                        'error': 'No se pueden filtrar fechas futuras'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Filtrar por fecha de preparación
                historial_query = historial_query.filter(
                    fecha_preparacion__date__range=[fecha_inicio, fecha_fin]
                )
            
            # Agrupar por receta y contar total de preparaciones
            from django.db.models import Count, Sum, Max
            recetas_agrupadas = historial_query.values(
                'receta_id',
                'receta__nombre',
                'receta__rinde',
                'receta__unidad_rinde',
                'receta__costo_total',
                'receta__precio_venta',
                'receta__veces_hecha_hoy'
            ).annotate(
                total_preparaciones=Sum('cantidad_preparada'),
                ultima_preparacion=Max('fecha_preparacion')  # ✅ Fecha de la última preparación
            ).order_by('-ultima_preparacion')  # Ordenar por la más reciente
            
            # Preparar datos para la respuesta
            recetas_data = []
            for grupo in recetas_agrupadas:
                recetas_data.append({
                    'id': grupo['receta_id'],
                    'nombre': grupo['receta__nombre'],
                    'cantidad': grupo['total_preparaciones'],  # Total de preparaciones en el período
                    'rinde': grupo['receta__rinde'],
                    'unidad_rinde': grupo['receta__unidad_rinde'],
                    'costo_total': float(grupo['receta__costo_total']) if grupo['receta__costo_total'] else 0,
                    'precio_venta': float(grupo['receta__precio_venta']) if grupo['receta__precio_venta'] else 0,
                    'veces_hecha_hoy': grupo['receta__veces_hecha_hoy'],
                    'ultima_preparacion': grupo['ultima_preparacion'].isoformat() if grupo['ultima_preparacion'] else None
                })
            
            return Response({
                'fecha_inicio': fecha_inicio_str,
                'fecha_fin': fecha_fin_str,
                'total_preparaciones': len(recetas_data),
                'recetas': recetas_data
            })
            
        except Exception as e:
            print(f"❌ Error en RecetasPorFechaView: {str(e)}")
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
                alignment=1,  # Centrado
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
            historial_query = HistorialReceta.objects.select_related('receta')
            
            if fecha_inicio_str and fecha_fin_str:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
                historial_query = historial_query.filter(
                    fecha_preparacion__date__range=[fecha_inicio, fecha_fin]
                )
            
            # Agrupar por receta
            from django.db.models import Count, Sum, Max
            recetas_agrupadas = historial_query.values(
                'receta_id',
                'receta__nombre',
                'receta__rinde',
                'receta__unidad_rinde',
                'receta__costo_total',
                'receta__precio_venta'
            ).annotate(
                total_preparaciones=Sum('cantidad_preparada'),
                ultima_preparacion=Max('fecha_preparacion')
            ).order_by('-total_preparaciones')
            
            # Preparar datos para la tabla
            if recetas_agrupadas:
                # Encabezados de la tabla
                data = [['Receta', 'Preparaciones', 'Costo Total', 'Precio Venta', 'Última Preparación']]
                
                for grupo in recetas_agrupadas:
                    # Formatear datos
                    nombre = grupo['receta__nombre']
                    preparaciones = str(grupo['total_preparaciones'])
                    costo_total = f"${grupo['receta__costo_total']:.2f}" if grupo['receta__costo_total'] else "$0.00"
                    precio_venta = f"${grupo['receta__precio_venta']:.2f}" if grupo['receta__precio_venta'] else "$0.00"
                    
                    # Formatear fecha
                    if grupo['ultima_preparacion']:
                        ultima_prep = grupo['ultima_preparacion'].strftime('%d/%m/%Y %H:%M')
                    else:
                        ultima_prep = "N/A"
                    
                    data.append([nombre, preparaciones, costo_total, precio_venta, ultima_prep])
                
                # Crear tabla
                table = Table(data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch, 1.5*inch])
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
                total_recetas = len(recetas_agrupadas)
                total_preparaciones = sum(grupo['total_preparaciones'] for grupo in recetas_agrupadas)
                
                summary_style = ParagraphStyle(
                    'CustomSummary',
                    parent=styles['Normal'],
                    fontSize=11,
                    spaceAfter=10,
                    textColor=colors.HexColor('#2c3e50')
                )
                
                elements.append(Paragraph(f"Total de recetas diferentes: {total_recetas}", summary_style))
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
# 🔹 Cierre Diario - VERSIÓN CORREGIDA
# -------------------------
class CierreDiarioView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            with transaction.atomic():
                # Obtener fecha actual
                hoy = timezone.now().date()
                print(f"🔹 Iniciando cierre diario para {hoy}")
                
                # Obtener todas las recetas con actividad hoy
                recetas_con_actividad = Receta.objects.filter(veces_hecha_hoy__gt=0)
                print(f"🔹 Recetas con actividad: {recetas_con_actividad.count()}")
                
                if not recetas_con_actividad.exists():
                    print("🔹 No hay recetas con actividad para cerrar")
                    return Response({
                        'mensaje': 'No hay recetas preparadas hoy para cerrar',
                        'cierre_realizado': False
                    }, status=status.HTTP_200_OK)
                
                # Realizar cierre diario
                recetas_procesadas = []
                total_preparaciones = 0
                
                for receta in recetas_con_actividad:
                    print(f"🔹 Procesando receta: {receta.nombre} - Preparaciones: {receta.veces_hecha_hoy}")
                    
                    # Crear registro en historial si se preparó hoy
                    if receta.veces_hecha_hoy > 0:
                        historial = HistorialReceta.objects.create(
                            receta=receta,
                            cantidad_preparada=receta.veces_hecha_hoy,
                            fecha_preparacion=timezone.now()
                        )
                        print(f"🔹 Historial creado: {historial.id}")
                        
                        recetas_procesadas.append({
                            'id': receta.id,
                            'nombre': receta.nombre,
                            'preparaciones': receta.veces_hecha_hoy
                        })
                        total_preparaciones += receta.veces_hecha_hoy
                    
                    # Guardar el valor antes de reiniciar para logging
                    valor_anterior = receta.veces_hecha_hoy
                    
                    # Reiniciar contador diario
                    receta.veces_hecha_hoy = 0
                    receta.ultima_actualizacion_diaria = hoy
                    receta.save(update_fields=['veces_hecha_hoy', 'ultima_actualizacion_diaria'])
                    
                    print(f"🔹 Receta {receta.nombre} reiniciada: {valor_anterior} → 0")
                
                print(f"🔹 Cierre diario completado. Total: {total_preparaciones} preparaciones")
                
                return Response({
                    'mensaje': f'Cierre diario realizado exitosamente',
                    'cierre_realizado': True,
                    'fecha_cierre': hoy.isoformat(),
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