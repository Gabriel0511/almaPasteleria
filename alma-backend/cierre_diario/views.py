# cierre_diario/views.py - CORREGIR
from django.utils import timezone
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta
from pedidos.models import Pedido
from recetas.models import Receta
from django.contrib.auth import get_user_model
User = get_user_model()
from insumos.models import HistorialStock, Insumo 
from .models import HistorialCierreDia, HistorialRecetasDia, HistorialPedidosDia, HistorialInsumosUtilizados

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_estado_cierre_dia(request):
    """Obtiene el estado del cierre del día actual"""
    try:
        fecha_hoy = timezone.now().date()
        
        # Verificar si ya se realizó el cierre hoy
        cierre_existente = HistorialCierreDia.objects.filter(
            fecha=fecha_hoy
        ).exists()
        
        # Obtener estadísticas del día actual
        recetas_preparadas = Receta.objects.filter(
            veces_hecha_hoy__gt=0
        ).count()
        
        pedidos_entregados = Pedido.objects.filter(
            estado='entregado',
            fecha_entrega__date=fecha_hoy
        ).count()
        
        # ✅ CORREGIDO: Usar HistorialStock en lugar de MovimientoStock
        insumos_utilizados = HistorialStock.objects.filter(
            fecha__date=fecha_hoy,
            tipo_movimiento__in=['RECETA', 'INGREDIENTE_EXTRA']  # Solo movimientos de salida
        ).count()
        
        return Response({
            'fecha_actual': fecha_hoy.isoformat(),
            'cierre_realizado': cierre_existente,
            'estadisticas_dia': {
                'recetas_preparadas': recetas_preparadas,
                'pedidos_entregados': pedidos_entregados,
                'insumos_utilizados': insumos_utilizados,
                'hora_actual': timezone.now().strftime('%H:%M:%S')
            }
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def cerrar_dia_laboral(request):
    """
    Cierra el día laboral actual y reinicia contadores DIARIOS
    """
    try:
        fecha_cierre = timezone.now().date()
        
        # Verificar si ya se realizó el cierre hoy
        if HistorialCierreDia.objects.filter(fecha=fecha_cierre).exists():
            return Response({
                'success': False,
                'error': f'El día {fecha_cierre} ya fue cerrado'
            }, status=400)
        
        # Crear registro principal del cierre
        cierre_dia = HistorialCierreDia.objects.create(
            fecha=fecha_cierre,
            usuario=request.user
        )
        
        # 1. Procesar recetas preparadas hoy (solo las que tienen veces_hecha_hoy > 0)
        recetas_hoy = Receta.objects.filter(veces_hecha_hoy__gt=0)
        for receta in recetas_hoy:
            HistorialRecetasDia.objects.create(
                cierre_dia=cierre_dia,
                receta=receta,
                cantidad_preparada=receta.veces_hecha_hoy,
                empleado=request.user
            )
        
        cierre_dia.recetas_registradas = recetas_hoy.count()
        
        # 2. Procesar pedidos entregados hoy
        pedidos_hoy = Pedido.objects.filter(
            estado='entregado',
            fecha_entrega__date=fecha_cierre
        )
        for pedido in pedidos_hoy:
            HistorialPedidosDia.objects.create(
                cierre_dia=cierre_dia,
                pedido=pedido,
                cliente_nombre=pedido.cliente.nombre,
                total=pedido.total
            )
        
        cierre_dia.pedidos_registrados = pedidos_hoy.count()
        
        # 3. ✅ CORREGIDO: Procesar insumos utilizados hoy usando HistorialStock
        movimientos_hoy = HistorialStock.objects.filter(
            fecha__date=fecha_cierre,
            tipo_movimiento__in=['RECETA', 'INGREDIENTE_EXTRA']  # Solo movimientos de salida
        )
        for movimiento in movimientos_hoy:
            HistorialInsumosUtilizados.objects.create(
                cierre_dia=cierre_dia,
                insumo=movimiento.insumo,
                cantidad_utilizada=movimiento.cantidad,
                motivo=movimiento.get_tipo_movimiento_display()  # Descripción legible
            )
        
        cierre_dia.insumos_registrados = movimientos_hoy.count()
        cierre_dia.save()
        
        # 4. ✅ REINICIAR SOLO CONTADORES DIARIOS (no el histórico)
        Receta.objects.all().update(veces_hecha_hoy=0)
        
        # 5. ✅ CORREGIDO: No hay que limpiar HistorialStock ya que es permanente
        # El HistorialStock se mantiene para auditoría
        
        return Response({
            'success': True,
            'message': f'Día laboral {fecha_cierre} cerrado correctamente',
            'resumen': {
                'recetas_preparadas': recetas_hoy.count(),
                'pedidos_entregados': pedidos_hoy.count(),
                'insumos_utilizados': movimientos_hoy.count()
            },
            'cierre_id': cierre_dia.id
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_historial_cierres(request):
    """Obtiene el historial de cierres diarios"""
    try:
        cierres = HistorialCierreDia.objects.all().order_by('-fecha')[:30]  # Últimos 30 días
        
        historial_data = []
        for cierre in cierres:
            historial_data.append({
                'fecha': cierre.fecha.isoformat(),
                'usuario': cierre.usuario.username,
                'recetas_registradas': cierre.recetas_registradas,
                'pedidos_registrados': cierre.pedidos_registrados,
                'insumos_registrados': cierre.insumos_registrados,
                'fecha_cierre': cierre.fecha_cierre
            })
        
        return Response({
            'historial': historial_data
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)
    
# cierre_diario/views.py - AGREGAR
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generar_reporte_diario_pdf(request):
    """Genera un PDF del reporte diario"""
    # Aquí implementas la generación del PDF
    # Puedes usar reportlab, weasyprint, etc.
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pre_reporte_diario(request):
    """Vista previa del reporte diario en JSON"""
    fecha = request.GET.get('fecha', timezone.now().date().isoformat())
    
    try:
        cierre = HistorialCierreDia.objects.get(fecha=fecha)
        recetas = HistorialRecetasDia.objects.filter(cierre_dia=cierre)
        pedidos = HistorialPedidosDia.objects.filter(cierre_dia=cierre)
        insumos = HistorialInsumosUtilizados.objects.filter(cierre_dia=cierre)
        
        return Response({
            'fecha': fecha,
            'resumen': {
                'recetas': cierre.recetas_registradas,
                'pedidos': cierre.pedidos_registrados,
                'insumos': cierre.insumos_registrados
            },
            'detalle_recetas': [
                {
                    'nombre': r.receta.nombre,
                    'cantidad': r.cantidad_preparada
                } for r in recetas
            ],
            'detalle_pedidos': [
                {
                    'cliente': p.cliente_nombre,
                    'total': float(p.total)
                } for p in pedidos
            ]
        })
        
    except HistorialCierreDia.DoesNotExist:
        return Response({'error': 'No existe cierre para esta fecha'}, status=404)