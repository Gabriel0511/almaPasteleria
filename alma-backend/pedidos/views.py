from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from django.utils import timezone
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from .models import Pedido, DetallePedido, Cliente, IngredientesExtra
from .serializers import IngredientesExtraWriteSerializer, PedidoWriteSerializer, PedidoReadSerializer, DetallePedidoWriteSerializer, DetallePedidoReadSerializer, ClienteSerializer
from recetas.models import Receta
from insumos.models import Insumo
from django.db.models import Count 
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

class PedidosHoyView(APIView):
    def get(self, request):
        hoy = date.today()
        
        # Entregar hoy: pedidos con fecha_entrega = hoy
        entregar_hoy = Pedido.objects.filter(
            fecha_entrega=hoy,
            estado__in=['pendiente', 'listo']
        )
        
        # Hacer hoy: pedidos con fecha_entrega en los próximos 3 días (hoy+1, hoy+2, hoy+3)
        fecha_limite = hoy + timedelta(days=3)
        hacer_hoy = Pedido.objects.filter(
            fecha_entrega__range=[hoy + timedelta(days=1), fecha_limite],
            estado__in=['pendiente', 'listo']
        )
        
        entregar_serializer = PedidoReadSerializer(entregar_hoy, many=True)
        hacer_serializer = PedidoReadSerializer(hacer_hoy, many=True)
        
        return Response({
            'entregar_hoy': entregar_serializer.data,
            'hacer_hoy': hacer_serializer.data
        }, status=status.HTTP_200_OK)

class ActualizarEstadoPedidoView(APIView):
    def patch(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        nuevo_estado = request.data.get('estado')
        
        # Validar transición de estado
        if pedido.estado in ['pendiente', 'listo'] and nuevo_estado == 'entregado':
            pedido.estado = 'entregado'
            pedido.save()
        elif pedido.estado == 'pendiente' and nuevo_estado == 'listo':
            pedido.estado = 'listo'
            pedido.save()
        else:
            return Response(
                {'error': 'Transición de estado no válida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(PedidoReadSerializer(pedido).data, status=status.HTTP_200_OK)

class PedidoListCreateAPIView(generics.ListCreateAPIView):
    queryset = Pedido.objects.all().order_by('-fecha_pedido')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PedidoReadSerializer
        return PedidoWriteSerializer
    
    def perform_create(self, serializer):
        # Guardar la fecha exacta como viene del frontend
        fecha_entrega_str = self.request.data.get('fecha_entrega')
        if fecha_entrega_str:
            # Parsear la fecha sin conversión de zona horaria
            from datetime import datetime
            fecha_entrega = datetime.strptime(fecha_entrega_str, '%Y-%m-%d').date()
            serializer.save(fecha_entrega=fecha_entrega)
        else:
            serializer.save()

class PedidoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pedido.objects.all()
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PedidoReadSerializer
        return PedidoWriteSerializer
    
class DetallePedidoCreateAPIView(generics.CreateAPIView):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoWriteSerializer

class DetallePedidoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DetallePedido.objects.all()
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DetallePedidoReadSerializer
        return DetallePedidoWriteSerializer

class ClienteListCreateAPIView(generics.ListCreateAPIView):
    queryset = Cliente.objects.all().order_by('nombre')
    serializer_class = ClienteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            {
                'message': 'Cliente creado exitosamente',
                'cliente': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class PedidosPorFechaView(APIView):
    def get(self, request):
        fecha_str = request.GET.get('fecha')
        if not fecha_str:
            return Response(
                {'error': 'Parámetro fecha requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fecha = date.fromisoformat(fecha_str)
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pedidos = Pedido.objects.filter(fecha_entrega=fecha)
        serializer = PedidoReadSerializer(pedidos, many=True)  # ← Cambiado
        
        return Response({
            'fecha': fecha_str,
            'pedidos': serializer.data,
            'total': pedidos.count()
        })

class PedidosPorEstadoView(APIView):
    def get(self, request):
        estado = request.GET.get('estado')
        if not estado:
            return Response(
                {'error': 'Parámetro estado requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if estado not in dict(Pedido.ESTADO_PEDIDO):
            return Response(
                {'error': 'Estado no válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pedidos = Pedido.objects.filter(estado=estado)
        serializer = PedidoReadSerializer(pedidos, many=True)  # ← Cambiado
        
        return Response({
            'estado': estado,
            'pedidos': serializer.data,
            'total': pedidos.count()
        })
    
class IngredientesExtraCreateAPIView(generics.CreateAPIView):
    queryset = IngredientesExtra.objects.all()
    serializer_class = IngredientesExtraWriteSerializer  # ← Cambiado

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            {
                'message': 'Ingrediente extra agregado exitosamente',
                'ingrediente_extra': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class IngredientesExtraRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = IngredientesExtra.objects.all()
    serializer_class = IngredientesExtraWriteSerializer  # ← Cambiado
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return Response(
            {
                'message': 'Ingrediente extra eliminado exitosamente',
                'ingrediente_extra_id': instance.id
            },
            status=status.HTTP_204_NO_CONTENT
        )
    
class EliminarDetallesPedidoView(APIView):
    def delete(self, request, pk):
        try:
            pedido = Pedido.objects.get(pk=pk)
            pedido.detalles.all().delete()
            return Response(
                {'message': 'Detalles del pedido eliminados exitosamente'},
                status=status.HTTP_200_OK
            )
        except Pedido.DoesNotExist:
            return Response(
                {'error': 'Pedido no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
class PedidosEntregadosView(APIView):
    def get(self, request):
        # Obtener parámetros de fecha
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        
        print(f"🔍 PedidosEntregadosView - Fecha inicio: {fecha_inicio}, Fecha fin: {fecha_fin}")
        
        # Filtrar solo pedidos entregados
        pedidos = Pedido.objects.filter(estado='entregado')\
                       .select_related('cliente')\
                       .prefetch_related('detalles__receta', 'detalles__ingredientes_extra')\
                       .order_by('-fecha_entrega')
        
        # Aplicar filtros de fecha si se proporcionan
        if fecha_inicio:
            try:
                fecha_inicio_obj = date.fromisoformat(fecha_inicio)
                # 🔹 SOLUCIÓN: Si solo hay fecha_inicio, buscar solo ese día (no desde esa fecha)
                if not fecha_fin:
                    # Filtra solo por ese día específico
                    pedidos = pedidos.filter(fecha_entrega=fecha_inicio_obj)
                    print(f"🔍 Solo fecha inicio: Filtrando EXACTAMENTE para {fecha_inicio_obj}")
                else:
                    # Si hay fecha_fin, usa rango >=
                    pedidos = pedidos.filter(fecha_entrega__gte=fecha_inicio_obj)
                    print(f"🔍 Con fecha fin: Filtrando desde {fecha_inicio_obj}")
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_inicio inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if fecha_fin:
            try:
                fecha_fin_obj = date.fromisoformat(fecha_fin)
                # 🔹 SOLUCIÓN: Si hay fecha_fin, usar <= para el rango
                pedidos = pedidos.filter(fecha_entrega__lte=fecha_fin_obj)
                print(f"🔍 Aplicando filtro fecha_fin: {fecha_fin_obj}")
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_fin inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        print(f"🔍 Total pedidos encontrados: {pedidos.count()}")
        
        # Serializar los datos
        serializer = PedidoReadSerializer(pedidos, many=True)
        
        return Response({
            'pedidos': serializer.data,
            'total': pedidos.count(),
            'filtros_aplicados': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            }
        })

class GenerarPDFPedidosView(APIView):
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
            title_text = "Reporte de Pedidos Entregados"
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
            
            # Obtener datos usando la misma lógica que PedidosEntregadosView
            pedidos = Pedido.objects.filter(estado='entregado')\
                           .prefetch_related('detalles__receta', 'detalles__ingredientes_extra')\
                           .order_by('-fecha_entrega')
            
            # Aplicar filtros de fecha si se proporcionan
            if fecha_inicio_str:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                pedidos = pedidos.filter(fecha_entrega__gte=fecha_inicio)
            
            if fecha_fin_str:
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
                pedidos = pedidos.filter(fecha_entrega__lte=fecha_fin)
            
            # Preparar datos para la tabla
            if pedidos:
                # Encabezados de la tabla
                data = [['Pedido ID', 'Cliente', 'Recetas', 'Fecha Entrega', 'Total']]
                
                total_general = 0
                
                for pedido in pedidos:
                    # Formatear datos
                    pedido_id = f"#{pedido.id}"
                    cliente = pedido.cliente.nombre if pedido.cliente else "Sin cliente"
                    
                    # Obtener recetas del pedido
                    recetas_text = ""
                    for detalle in pedido.detalles.all():
                        receta_nombre = detalle.receta.nombre if detalle.receta else "Receta no disponible"
                        cantidad = detalle.cantidad
                        recetas_text += f"{receta_nombre} (x{cantidad}), "
                    
                    # Remover última coma y espacio
                    recetas_text = recetas_text.rstrip(', ')
                    
                    # Limitar longitud del texto de recetas
                    if len(recetas_text) > 50:
                        recetas_text = recetas_text[:47] + "..."
                    
                    fecha_entrega = pedido.fecha_entrega.strftime('%d/%m/%Y') if pedido.fecha_entrega else "N/A"
                    total = f"${pedido.total:.2f}" if pedido.total else "$0.00"
                    
                    data.append([pedido_id, cliente, recetas_text, fecha_entrega, total])
                    
                    # Sumar al total general
                    if pedido.total:
                        total_general += pedido.total
                
                # Crear tabla
                table = Table(data, colWidths=[0.8*inch, 1.5*inch, 2.5*inch, 1*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Alinear recetas a la izquierda
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
                ]))
                
                elements.append(table)
                
                # Agregar resumen
                elements.append(Spacer(1, 20))
                
                summary_style = ParagraphStyle(
                    'CustomSummary',
                    parent=styles['Normal'],
                    fontSize=11,
                    spaceAfter=10,
                    textColor=colors.HexColor('#2c3e50')
                )
                
                elements.append(Paragraph(f"Total de pedidos entregados: {len(pedidos)}", summary_style))
                elements.append(Paragraph(f"Total general: ${total_general:.2f}", summary_style))
                
                # Agregar desglose por día si hay múltiples fechas
                if fecha_inicio_str and fecha_fin_str:
                    from django.db.models import Sum
                    pedidos_por_dia = pedidos.values('fecha_entrega').annotate(
                        total_dia=Sum('total'),
                        cantidad=Count('id')
                    ).order_by('fecha_entrega')
                    
                    if len(pedidos_por_dia) > 1:
                        elements.append(Spacer(1, 15))
                        elements.append(Paragraph("Desglose por día:", summary_style))
                        
                        for dia in pedidos_por_dia:
                            fecha_dia = dia['fecha_entrega'].strftime('%d/%m/%Y')
                            elements.append(Paragraph(
                                f"  {fecha_dia}: {dia['cantidad']} pedidos - ${dia['total_dia']:.2f}", 
                                summary_style
                            ))
                
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
                elements.append(Paragraph("No hay pedidos entregados en el período seleccionado", no_data_style))
            
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
                filename = f"pedidos_entregados_{fecha_inicio_str}_a_{fecha_fin_str}.pdf"
            else:
                filename = f"pedidos_entregados_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            print(f"❌ Error en GenerarPDFPedidosView: {str(e)}")
            return Response({
                'error': f'Error al generar PDF: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)