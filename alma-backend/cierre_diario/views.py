# cierre_diario/views.py - CORREGIDO
from django.utils import timezone
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta
from pedidos.models import Pedido
from recetas.models import Receta
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
        
        # Usar HistorialStock para insumos utilizados
        insumos_utilizados = HistorialStock.objects.filter(
            fecha__date=fecha_hoy,
            tipo_movimiento__in=['RECETA', 'INGREDIENTE_EXTRA']
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
        print(f"❌ Error en obtener_estado_cierre_dia: {str(e)}")
        return Response({
            'error': f'Error interno del servidor: {str(e)}'
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
        
        print(f"🔧 Iniciando cierre del día: {fecha_cierre}")
        
        # Verificar si ya se realizó el cierre hoy
        if HistorialCierreDia.objects.filter(fecha=fecha_cierre).exists():
            return Response({
                'success': False,
                'error': f'El día {fecha_cierre} ya fue cerrado'
            }, status=400)
        
        # Crear registro principal del cierre (SIN usuario)
        cierre_dia = HistorialCierreDia.objects.create(
            fecha=fecha_cierre
        )
        
        print(f"📝 Cierre creado: {cierre_dia.id}")
        
        # 1. Procesar recetas preparadas hoy (SIN empleado)
        recetas_hoy = Receta.objects.filter(veces_hecha_hoy__gt=0)
        print(f"👨‍🍳 Recetas hoy: {recetas_hoy.count()}")
        
        for receta in recetas_hoy:
            HistorialRecetasDia.objects.create(
                cierre_dia=cierre_dia,
                receta=receta,
                cantidad_preparada=receta.veces_hecha_hoy
                # ✅ SIN empleado
            )
        
        cierre_dia.recetas_registradas = recetas_hoy.count()
        
        # 2. Procesar pedidos entregados hoy
        pedidos_hoy = Pedido.objects.filter(
            estado='entregado',
            fecha_entrega__date=fecha_cierre
        )
        print(f"📦 Pedidos hoy: {pedidos_hoy.count()}")
        
        for pedido in pedidos_hoy:
            HistorialPedidosDia.objects.create(
                cierre_dia=cierre_dia,
                pedido=pedido,
                cliente_nombre=pedido.cliente.nombre,
                total=pedido.total
            )
        
        cierre_dia.pedidos_registrados = pedidos_hoy.count()
        
        # 3. Procesar insumos utilizados hoy
        movimientos_hoy = HistorialStock.objects.filter(
            fecha__date=fecha_cierre,
            tipo_movimiento__in=['RECETA', 'INGREDIENTE_EXTRA']
        )
        print(f"📊 Movimientos hoy: {movimientos_hoy.count()}")
        
        for movimiento in movimientos_hoy:
            HistorialInsumosUtilizados.objects.create(
                cierre_dia=cierre_dia,
                insumo=movimiento.insumo,
                cantidad_utilizada=movimiento.cantidad,
                motivo=movimiento.get_tipo_movimiento_display()
            )
        
        cierre_dia.insumos_registrados = movimientos_hoy.count()
        cierre_dia.save()
        
        # 4. REINICIAR CONTADORES DIARIOS
        Receta.objects.all().update(veces_hecha_hoy=0)
        print("🔄 Contadores diarios reiniciados")
        
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
        print(f"❌ Error en cerrar_dia_laboral: {str(e)}")
        return Response({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_historial_cierres(request):
    """Obtiene el historial de cierres diarios"""
    try:
        cierres = HistorialCierreDia.objects.all().order_by('-fecha')[:30]
        
        historial_data = []
        for cierre in cierres:
            historial_data.append({
                'fecha': cierre.fecha.isoformat(),
                # ✅ SIN usuario
                'recetas_registradas': cierre.recetas_registradas,
                'pedidos_registrados': cierre.pedidos_registrados,
                'insumos_registrados': cierre.insumos_registrados,
                'fecha_cierre': cierre.fecha_cierre
            })
        
        return Response({
            'historial': historial_data
        })
        
    except Exception as e:
        print(f"❌ Error en obtener_historial_cierres: {str(e)}")
        return Response({
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pre_reporte_diario(request):
    """Vista previa del reporte diario en JSON"""
    try:
        fecha = request.GET.get('fecha', timezone.now().date().isoformat())
        
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
            ],
            'detalle_insumos': [
                {
                    'nombre': i.insumo.nombre,
                    'cantidad': float(i.cantidad_utilizada),
                    'unidad': i.insumo.unidad_medida.abreviatura,
                    'motivo': i.motivo
                } for i in insumos
            ]
        })
        
    except HistorialCierreDia.DoesNotExist:
        return Response({'error': 'No existe cierre para esta fecha'}, status=404)
    except Exception as e:
        print(f"❌ Error en pre_reporte_diario: {str(e)}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generar_reporte_diario_pdf(request):
    """Genera un PDF del reporte diario (placeholder)"""
    try:
        fecha = request.GET.get('fecha', timezone.now().date().isoformat())
        
        # Por ahora devolvemos un JSON, luego implementas PDF
        cierre = HistorialCierreDia.objects.get(fecha=fecha)
        
        return Response({
            'message': 'PDF generado correctamente',
            'fecha': fecha,
            'resumen': {
                'recetas': cierre.recetas_registradas,
                'pedidos': cierre.pedidos_registrados,
                'insumos': cierre.insumos_registrados
            }
        })
        
    except HistorialCierreDia.DoesNotExist:
        return Response({'error': 'No existe cierre para esta fecha'}, status=404)
    except Exception as e:
        print(f"❌ Error en generar_reporte_diario_pdf: {str(e)}")
        return Response({'error': str(e)}, status=500)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recetas_por_fecha(request):
    """Obtiene las recetas hechas en una fecha específica desde el historial"""
    try:
        fecha_param = request.GET.get('fecha')
        if not fecha_param:
            return Response({'error': 'El parámetro fecha es requerido'}, status=400)
        
        # Convertir fecha
        fecha = timezone.datetime.strptime(fecha_param, '%Y-%m-%d').date()
        
        # Buscar el cierre del día para esa fecha
        try:
            cierre_dia = HistorialCierreDia.objects.get(fecha=fecha)
        except HistorialCierreDia.DoesNotExist:
            # Si no hay cierre para esa fecha, devolver array vacío
            return Response({
                'fecha': fecha.isoformat(),
                'total_recetas': 0,
                'recetas': []
            })
        
        # Obtener las recetas del historial para esa fecha
        recetas_historial = HistorialRecetasDia.objects.filter(
            cierre_dia=cierre_dia
        ).select_related('receta')  # ✅ SIN empleado
        
        # Preparar datos para la respuesta
        recetas_data = []
        for rh in recetas_historial:
            recetas_data.append({
                'id': rh.id,
                'receta_id': rh.receta.id,
                'nombre': rh.receta.nombre,
                'cantidad': rh.cantidad_preparada,
                'fecha': fecha.isoformat(),
                'hora': rh.cierre_dia.fecha_cierre.strftime('%H:%M:%S'),
                'estado': 'Completado',
                # ✅ SIN empleado
                'rinde': rh.receta.rinde,
                'unidad_rinde': rh.receta.unidad_rinde,
                'costo_total': float(rh.receta.costo_total) if rh.receta.costo_total else 0,
                'precio_venta': float(rh.receta.precio_venta) if rh.receta.precio_venta else 0
            })
        
        return Response({
            'fecha': fecha.isoformat(),
            'total_recetas': len(recetas_data),
            'recetas': recetas_data
        })
        
    except ValueError:
        return Response({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=400)
    except Exception as e:
        print(f"❌ Error en recetas_por_fecha: {str(e)}")
        return Response({
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)