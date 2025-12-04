# views.py - Versión COMPLETA y corregida
from django.db.models import F
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse, JsonResponse
from .models import Insumo, UnidadMedida, CategoriaInsumo, Proveedor, Perdida, HistorialStock
from .serializers import InsumoSerializer, UnidadMedidaSerializer, CategoriaInsumoSerializer, ProveedorSerializer, PerdidaSerializer, PerdidaCreateSerializer
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Q
from django.db import models
from datetime import datetime, timedelta, date
from decimal import Decimal
import io
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ==================== VISTAS PARA UNIDADES DE MEDIDA ====================
class UnidadMedidaListAPIView(generics.ListAPIView):
    queryset = UnidadMedida.objects.all()
    serializer_class = UnidadMedidaSerializer

class UnidadMedidaDetailAPIView(generics.RetrieveAPIView):
    queryset = UnidadMedida.objects.all()
    serializer_class = UnidadMedidaSerializer

class UnidadMedidaCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = UnidadMedida.objects.all()
    serializer_class = UnidadMedidaSerializer

    def create(self, request, *args, **kwargs):
        nombre = request.data.get('nombre', '').strip()
        if UnidadMedida.objects.filter(nombre__iexact=nombre).exists():
            return Response(
                {'error': 'Ya existe una unidad con este nombre'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'Unidad de Medida creada exitosamente',
                'unidad': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

# ==================== VISTAS PARA CATEGORÍAS ====================
class CategoriaInsumoListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CategoriaInsumo.objects.all()
    serializer_class = CategoriaInsumoSerializer

class CategoriaInsumoCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CategoriaInsumo.objects.all()
    serializer_class = CategoriaInsumoSerializer

    def create(self, request, *args, **kwargs):
        nombre = request.data.get('nombre', '').strip()
        if CategoriaInsumo.objects.filter(nombre__iexact=nombre).exists():
            return Response(
                {'error': 'Ya existe una categoría con este nombre'},
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

# ==================== VISTAS PARA PROVEEDORES ====================
class ProveedorListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class ProveedorCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

    def create(self, request, *args, **kwargs):
        nombre = request.data.get('nombre', '').strip()
        if Proveedor.objects.filter(nombre__iexact=nombre).exists():
            return Response(
                {'error': 'Ya existe un proveedor con este nombre'},
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

# ==================== VISTAS PARA INSUMOS ====================
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
        nombre = request.data.get('nombre', '').strip()
        
        # Buscar si existe un insumo con ese nombre (activo o inactivo)
        insumo_existente = Insumo.objects.filter(nombre__iexact=nombre).first()
        
        if insumo_existente:
            if insumo_existente.activo:
                return Response(
                    {'error': 'Ya existe un insumo activo con este nombre'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                # Insumo existe pero está desactivado
                return Response(
                    {
                        'error': 'insumo_desactivado',
                        'message': 'Ya existe un insumo con este nombre pero está desactivado',
                        'insumo_id': insumo_existente.id,
                        'nombre': insumo_existente.nombre
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

class InsumoDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.activo = False
        instance.save()
        return Response(
            {
                'message': 'Insumo eliminado exitosamente',
                'insumo_id': instance.id
            },
            status=status.HTTP_200_OK
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

# ==================== VISTAS PARA PÉRDIDAS ====================
class PerdidaListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Perdida.objects.all().order_by('-fecha', '-id')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PerdidaCreateSerializer
        return PerdidaSerializer
    
    def get_queryset(self):
        queryset = Perdida.objects.all().order_by('-fecha', '-id')
        
        # Filtros
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        insumo_id = self.request.query_params.get('insumo_id')
        motivo = self.request.query_params.get('motivo')
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
        if insumo_id:
            queryset = queryset.filter(insumo_id=insumo_id)
        if motivo:
            queryset = queryset.filter(motivo=motivo)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Validar que el insumo existe
            insumo_id = serializer.validated_data['insumo'].id
            insumo = Insumo.objects.get(id=insumo_id)
            
            # Validar que hay suficiente stock
            cantidad_perdida = serializer.validated_data['cantidad']
            if cantidad_perdida > insumo.stock_actual:
                return Response({
                    'error': f'No hay suficiente stock. Stock actual: {insumo.stock_actual}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear la pérdida (el save() del modelo actualizará el stock automáticamente)
            perdida = serializer.save()
            
            # Crear registro en el historial
            HistorialStock.objects.create(
                insumo=insumo,
                tipo_movimiento='PERDIDA',
                cantidad=-cantidad_perdida,  # Negativo porque es una salida
                unidad_medida=insumo.unidad_medida,
                descripcion=f"Pérdida registrada - Motivo: {perdida.get_motivo_display()}",
                perdida=perdida
            )
            
            # Devolver los datos completos
            response_serializer = PerdidaSerializer(perdida)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Insumo.DoesNotExist:
            return Response({'error': 'Insumo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PerdidaDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Perdida.objects.all()
    serializer_class = PerdidaSerializer

# ==================== VISTAS PARA REPORTES ====================
class ReporteInsumosAPIView(APIView):
    def get(self, request):
        try:
            # Obtener parámetros de filtro
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            proveedor_id = request.GET.get('proveedor_id')
            solo_con_stock_usado = request.GET.get('solo_con_stock_usado', 'false').lower() == 'true'
            
            # Validar fechas
            fecha_inicio_dt = None
            fecha_fin_dt = None
            
            if fecha_inicio:
                try:
                    fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Formato de fecha_inicio inválido. Use YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if fecha_fin:
                try:
                    fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Formato de fecha_fin inválido. Use YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Si solo una fecha está especificada, usar rango por defecto
            if fecha_inicio_dt and not fecha_fin_dt:
                fecha_fin_dt = fecha_inicio_dt + timedelta(days=30)  # Rango de 30 días
            elif fecha_fin_dt and not fecha_inicio_dt:
                fecha_inicio_dt = fecha_fin_dt - timedelta(days=30)  # Rango de 30 días
            
            # Filtrar insumos activos
            insumos = Insumo.objects.filter(activo=True)
            
            # Aplicar filtro por proveedor
            if proveedor_id:
                insumos = insumos.filter(proveedor_id=proveedor_id)
            
            reporte_data = []
            for insumo in insumos:
                # Calcular stock usado desde recetas
                stock_usado_recetas = self.calcular_stock_usado_recetas(insumo, fecha_inicio_dt, fecha_fin_dt)
                
                # Calcular stock usado desde ingredientes extra
                stock_usado_ingredientes_extra = self.calcular_stock_usado_ingredientes_extra(insumo, fecha_inicio_dt, fecha_fin_dt)
                
                # Stock total usado
                stock_usado_total = stock_usado_recetas + stock_usado_ingredientes_extra

                 # Si se solicita solo con stock usado y el total es 0, omitir
                if solo_con_stock_usado and stock_usado_total == 0:
                    continue
                
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
            from recetas.models import RecetaInsumo
            
            # Obtener todas las recetas que usan este insumo
            recetas_insumos = RecetaInsumo.objects.filter(insumo=insumo)
            
            stock_usado_total = Decimal('0.0')
            
            for receta_insumo in recetas_insumos:
                receta = receta_insumo.receta
                
                # Calcular veces hechas en el período basado en pedidos
                veces_en_periodo = self.calcular_veces_receta_en_periodo(receta, fecha_inicio, fecha_fin)
                
                # Calcular cantidad usada por receta
                cantidad_por_receta = receta_insumo.get_cantidad_en_unidad_insumo()
                stock_usado = cantidad_por_receta * Decimal(str(veces_en_periodo))
                stock_usado_total += stock_usado
            
            return stock_usado_total
            
        except Exception as e:
            print(f"Error calculando stock usado en recetas: {e}")
            return Decimal('0.0')
    
    def calcular_veces_receta_en_periodo(self, receta, fecha_inicio, fecha_fin):
        """
        Calcula cuántas veces se usó una receta en un período específico
        """
        try:
            from pedidos.models import DetallePedido
            
            if fecha_inicio and fecha_fin:
                # Contar la cantidad total de esta receta en pedidos del período
                veces = DetallePedido.objects.filter(
                    receta=receta,
                    pedido__fecha_entrega__range=[fecha_inicio, fecha_fin],
                    pedido__estado__in=['pendiente', 'listo', 'entregado']  # Pedidos activos
                ).aggregate(
                    total=Sum('cantidad')
                )['total'] or 0
            else:
                # Sin filtro de fecha, usar todas las veces hechas de la receta
                veces = receta.veces_hecha
            
            return veces
            
        except Exception as e:
            print(f"Error calculando veces receta en período: {e}")
            return receta.veces_hecha  # Fallback
    
    def calcular_stock_usado_ingredientes_extra(self, insumo, fecha_inicio, fecha_fin):
        """
        Calcula el stock usado por ingredientes extra para un insumo específico
        """
        try:
            from pedidos.models import IngredientesExtra
            
            # Filtrar ingredientes extra por insumo
            ingredientes_query = IngredientesExtra.objects.filter(insumo=insumo)
            
            # Aplicar filtro de fecha si existe
            if fecha_inicio and fecha_fin:
                ingredientes_query = ingredientes_query.filter(
                    detalle__pedido__fecha_entrega__range=[fecha_inicio, fecha_fin],
                    detalle__pedido__estado__in=['pendiente', 'listo', 'entregado']
                )
            
            # Sumar todas las cantidades de ingredientes extra
            stock_usado_total = Decimal('0.0')
            for ingrediente in ingredientes_query:
                # Convertir a la unidad del insumo si es necesario
                if ingrediente.unidad_medida != insumo.unidad_medida:
                    try:
                        # Usar el método de conversión del modelo UnidadMedida
                        cantidad_convertida = ingrediente.unidad_medida.convertir_a(
                            ingrediente.cantidad, 
                            insumo.unidad_medida
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

class ListaComprasAPIView(APIView):
    def get(self, request):
        try:
            # Obtener parámetros de filtro
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            proveedor_id = request.GET.get('proveedor_id')
            
            # Validar fechas
            fecha_inicio_dt = None
            fecha_fin_dt = None
            
            if fecha_inicio:
                try:
                    fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Formato de fecha_inicio inválido. Use YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if fecha_fin:
                try:
                    fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Formato de fecha_fin inválido. Use YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Si no se especifican fechas, usar la próxima semana por defecto
            if not fecha_inicio_dt and not fecha_fin_dt:
                hoy = timezone.now().date()
                # Encontrar el próximo lunes
                dias_hasta_lunes = (0 - hoy.weekday()) % 7
                if dias_hasta_lunes == 0:
                    dias_hasta_lunes = 7
                
                fecha_inicio_dt = hoy + timedelta(days=dias_hasta_lunes)
                fecha_fin_dt = fecha_inicio_dt + timedelta(days=6)
            elif fecha_inicio_dt and not fecha_fin_dt:
                fecha_fin_dt = fecha_inicio_dt + timedelta(days=6)
            elif fecha_fin_dt and not fecha_inicio_dt:
                fecha_inicio_dt = fecha_fin_dt - timedelta(days=6)
            
            # Filtrar insumos activos
            insumos = Insumo.objects.filter(activo=True)
            
            # Aplicar filtro por proveedor
            if proveedor_id:
                insumos = insumos.filter(proveedor_id=proveedor_id)
            
            lista_compras_data = []
            
            for insumo in insumos:
                # Calcular pedidos para el período seleccionado
                pedidos_periodo = self.calcular_pedidos_periodo(insumo, fecha_inicio_dt, fecha_fin_dt)
                
                stock_minimo = insumo.stock_minimo
                stock_actual = insumo.stock_actual
                total_comprar = max(Decimal('0.0'), (stock_minimo - stock_actual) + pedidos_periodo)
                        
                lista_compras_data.append({
                    'id': insumo.id,
                    'nombre': insumo.nombre,
                    'categoria': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                    'stock_actual': float(stock_actual),
                    'stock_minimo': float(stock_minimo),
                    'pedidos': float(pedidos_periodo),
                    'total_comprar': float(total_comprar),
                    'unidad_medida': {
                        'abreviatura': insumo.unidad_medida.abreviatura
                    },
                    'proveedor': {
                        'id': insumo.proveedor.id if insumo.proveedor else None,
                        'nombre': insumo.proveedor.nombre if insumo.proveedor else 'Sin proveedor'
                    } if insumo.proveedor else None,
                    'necesita_compra': total_comprar > 0
                })
            
            return Response(lista_compras_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al generar lista de compras: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def calcular_pedidos_periodo(self, insumo, fecha_inicio, fecha_fin):
        """
        Calcula los pedidos para un período específico
        """
        try:
            from pedidos.models import DetallePedido, IngredientesExtra
            from recetas.models import RecetaInsumo
            
            # Calcular pedidos de recetas para el período
            pedidos_recetas = Decimal('0.0')
            
            # Obtener todos los detalles de pedido en el período
            detalles_pedido = DetallePedido.objects.filter(
                pedido__fecha_entrega__range=[fecha_inicio, fecha_fin],
                pedido__estado__in=['pendiente', 'listo']  # Solo pedidos activos
            ).select_related('receta')
            
            for detalle in detalles_pedido:
                # Buscar si la receta usa este insumo
                try:
                    receta_insumo = RecetaInsumo.objects.get(
                        receta=detalle.receta,
                        insumo=insumo
                    )
                    # Calcular cantidad usada
                    cantidad_por_receta = receta_insumo.get_cantidad_en_unidad_insumo()
                    cantidad_total = cantidad_por_receta * Decimal(str(detalle.cantidad))
                    pedidos_recetas += cantidad_total
                except RecetaInsumo.DoesNotExist:
                    # Esta receta no usa este insumo
                    continue
            
            # Calcular ingredientes extra para el período
            pedidos_extra = IngredientesExtra.objects.filter(
                insumo=insumo,
                detalle__pedido__fecha_entrega__range=[fecha_inicio, fecha_fin],
                detalle__pedido__estado__in=['pendiente', 'listo']
            ).aggregate(
                total=Sum('cantidad')
            )['total'] or Decimal('0.0')
            
            # Convertir ingredientes extra a la unidad del insumo si es necesario
            if pedidos_extra > 0:
                ingredientes_extra = IngredientesExtra.objects.filter(
                    insumo=insumo,
                    detalle__pedido__fecha_entrega__range=[fecha_inicio, fecha_fin]
                )
                pedidos_extra_convertido = Decimal('0.0')
                for ingrediente in ingredientes_extra:
                    if ingrediente.unidad_medida != insumo.unidad_medida:
                        try:
                            cantidad_convertida = ingrediente.unidad_medida.convertir_a(
                                ingrediente.cantidad, 
                                insumo.unidad_medida
                            )
                            pedidos_extra_convertido += cantidad_convertida
                        except Exception:
                            pedidos_extra_convertido += ingrediente.cantidad
                    else:
                        pedidos_extra_convertido += ingrediente.cantidad
                pedidos_extra = pedidos_extra_convertido
            
            return pedidos_recetas + pedidos_extra
            
        except Exception as e:
            print(f"Error calculando pedidos para período: {e}")
            # En caso de error, usar una estimación conservadora
            return insumo.stock_minimo * Decimal('0.2')  # 20% del stock mínimo

class InsumoReactivarAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, id):
        try:
            insumo = Insumo.objects.get(id=id)
            if insumo.activo:
                return Response(
                    {'error': 'El insumo ya está activo'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Reactivar el insumo
            insumo.activo = True
            insumo.save()
            
            # Actualizar con los datos del formulario si se proporcionan
            serializer = InsumoSerializer(insumo, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
            
            return Response(
                {
                    'message': 'Insumo reactivado exitosamente',
                    'insumo': InsumoSerializer(insumo).data
                },
                status=status.HTTP_200_OK
            )
            
        except Insumo.DoesNotExist:
            return Response(
                {'error': 'Insumo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

# Vista simple alternativa para lista de compras
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_compras_simple(request):
    """
    Vista alternativa para lista de compras
    """
    try:
        # Calcular rango de fechas para la próxima semana
        hoy = timezone.now().date()
        
        # Encontrar el próximo lunes
        dias_hasta_lunes = (0 - hoy.weekday()) % 7
        if dias_hasta_lunes == 0:
            dias_hasta_lunes = 7
        
        # Obtener todos los insumos activos
        insumos = Insumo.objects.filter(activo=True).select_related('proveedor', 'unidad_medida', 'categoria')
        
        lista_compras_data = []
        
        for insumo in insumos:
            # Estimación simple de pedidos
            pedidos_proxima_semana = insumo.stock_minimo * Decimal('0.3')  # 30% del stock mínimo
            
            # Calcular cantidad total a comprar
            stock_minimo = insumo.stock_minimo
            stock_actual = insumo.stock_actual
            total_comprar = max(Decimal('0.0'), (stock_minimo - stock_actual) + pedidos_proxima_semana)
            
            lista_compras_data.append({
                'id': insumo.id,
                'nombre': insumo.nombre,
                'categoria': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                'stock_actual': float(stock_actual),
                'stock_minimo': float(stock_minimo),
                'pedidos': float(pedidos_proxima_semana),
                'total_comprar': float(total_comprar),
                'unidad_medida': {
                    'abreviatura': insumo.unidad_medida.abreviatura
                },
                'proveedor': {
                    'id': insumo.proveedor.id if insumo.proveedor else None,
                    'nombre': insumo.proveedor.nombre if insumo.proveedor else 'Sin proveedor'
                },
                # ELIMINADO: 'dia_compra': dia_compra,
                'necesita_compra': total_comprar > 0
            })
        
        return JsonResponse(lista_compras_data, safe=False)
        
    except Exception as e:
        return JsonResponse(
            {'error': f'Error al generar lista de compras: {str(e)}'},
            status=500
        )
    
class GenerarPDFReporteInsumosAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Obtener parámetros de filtro
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            proveedor_id = request.GET.get('proveedor_id')
            solo_con_stock_usado = request.GET.get('solo_con_stock_usado', 'true').lower() == 'true'
            
            print(f"DEBUG PDF - Parámetros recibidos:")
            print(f"  - solo_con_stock_usado: {solo_con_stock_usado}")
            print(f"  - fecha_inicio: {fecha_inicio}")
            print(f"  - fecha_fin: {fecha_fin}")
            print(f"  - proveedor_id: {proveedor_id}")
            
            # Obtener datos DIRECTAMENTE usando nuestra propia lógica
            reporte_data = self.obtener_datos_reporte_directo(fecha_inicio, fecha_fin, proveedor_id)
            
            print(f"DEBUG PDF - Datos obtenidos antes de filtrar: {len(reporte_data)} insumos")
            
            # Mostrar stock usado de cada insumo para debug
            for i, item in enumerate(reporte_data[:5]):  # Mostrar primeros 5
                print(f"  Insumo {i+1}: {item['nombre']} - Stock usado: {item['stock_usado']}")
            
            # Filtrar solo los insumos con stock usado > 0 si se solicita
            if solo_con_stock_usado:
                reporte_original = len(reporte_data)
                reporte_data = [item for item in reporte_data if item['stock_usado'] > 0]
                print(f"DEBUG PDF - Después de filtrar (stock_usado > 0): {len(reporte_data)} insumos")
                print(f"DEBUG PDF - Se eliminaron: {reporte_original - len(reporte_data)} insumos con stock usado = 0")
            
            # Crear el PDF
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=10,
                alignment=1,
                textColor=colors.HexColor('#7B5A50')
            )
            
            # Título principal
            title_text = "Reporte de Insumos Utilizados"
            
            # Subtítulo con fechas - FORMATO DD/MM/YYYY
            if fecha_inicio and fecha_fin:
                # Formatear fechas a DD/MM/YYYY
                fecha_inicio_fmt = self.formatear_fecha_dd_mm_yyyy(fecha_inicio)
                fecha_fin_fmt = self.formatear_fecha_dd_mm_yyyy(fecha_fin)
                
                subtitle_style = ParagraphStyle(
                    'Subtitle',
                    parent=styles['Normal'],
                    fontSize=12,
                    alignment=1,
                    textColor=colors.grey,
                    spaceAfter=10
                )
                elements.append(Paragraph(f"Período: {fecha_inicio_fmt} al {fecha_fin_fmt}", subtitle_style))
            
            elements.append(Paragraph(title_text, title_style))
            elements.append(Spacer(1, 20))
            
            # Si no hay datos después del filtro
            if not reporte_data:
                no_data_style = ParagraphStyle(
                    'NoData',
                    parent=styles['Normal'],
                    fontSize=12,
                    alignment=1,
                    textColor=colors.red,
                    spaceAfter=20
                )
                elements.append(Paragraph("No hay insumos con stock usado en el período seleccionado", no_data_style))
                
                # Agregar información de parámetros
                param_style = ParagraphStyle(
                    'ParamStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    alignment=1,
                    textColor=colors.grey
                )
                param_text = f"Filtro aplicado: solo_con_stock_usado={solo_con_stock_usado}"
                if fecha_inicio and fecha_fin:
                    fecha_inicio_fmt = self.formatear_fecha_dd_mm_yyyy(fecha_inicio)
                    fecha_fin_fmt = self.formatear_fecha_dd_mm_yyyy(fecha_fin)
                    param_text += f" | Período: {fecha_inicio_fmt} a {fecha_fin_fmt}"
                elements.append(Paragraph(param_text, param_style))
                
                doc.build(elements)
                buffer.seek(0)
                response = HttpResponse(buffer, content_type='application/pdf')
                filename = f"reporte_insumos_sin_stock_usado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            
            # Preparar datos para la tabla
            table_data = [['Insumo', 'Stock Usado', 'Stock Actual', 'Stock Mínimo', '¿Reponer?', 'Proveedor']]
            
            for item in reporte_data:
                necesita_reposicion = "SÍ" if item['necesita_reposicion'] else "NO"
                proveedor = item['proveedor']['nombre'] if item['proveedor'] else 'Sin proveedor'
                
                table_data.append([
                    f"{item['nombre']} ({item['categoria']})",
                    f"{item['stock_usado']:.3f} {item['unidad_medida']['abreviatura']}",
                    f"{item['stock_actual']:.3f} {item['unidad_medida']['abreviatura']}",
                    f"{item['stock_minimo']:.3f} {item['unidad_medida']['abreviatura']}",
                    necesita_reposicion,
                    proveedor
                ])
            
            # Crear tabla
            table = Table(table_data, colWidths=[2.2*inch, 1*inch, 1*inch, 1*inch, 0.8*inch, 1.5*inch])
            
            # Estilos de la tabla
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7B5A50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]
            
            # Aplicar color a las filas que necesitan reposición
            for i in range(1, len(table_data)):
                if reporte_data[i-1]['necesita_reposicion']:
                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8d7da')))
            
            table.setStyle(TableStyle(table_style))
            
            elements.append(table)
            
            # Agregar resumen
            elements.append(Spacer(1, 30))
            
            # Estadísticas
            total_insumos = len(reporte_data)
            insumos_reponer = len([item for item in reporte_data if item['necesita_reposicion']])
            
            resumen_text = f"Resumen: {total_insumos} insumos con stock usado | {insumos_reponer} necesitan reposición"
            resumen_style = ParagraphStyle(
                'Resumen',
                parent=styles['Normal'],
                fontSize=10,
                alignment=1,
                textColor=colors.HexColor('#7B5A50'),
                spaceBefore=10
            )
            elements.append(Paragraph(resumen_text, resumen_style))
            
            # Fecha de generación - FORMATO DD/MM/YYYY
            fecha_gen = ParagraphStyle(
                'FechaGen',
                parent=styles['Normal'],
                fontSize=8,
                alignment=1,
                textColor=colors.grey,
                spaceBefore=20
            )
            # Cambiado a DD/MM/YYYY
            elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", fecha_gen))
            
            # Construir PDF
            doc.build(elements)
            
            # Preparar respuesta
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            
            # Nombre del archivo
            filename = f"reporte_insumos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            if fecha_inicio and fecha_fin:
                # Mantener formato YYYYMMDD para el nombre del archivo (mejor para ordenar)
                fecha_inicio_archivo = fecha_inicio.replace("-", "")
                fecha_fin_archivo = fecha_fin.replace("-", "")
                filename = f"reporte_insumos_{fecha_inicio_archivo}_a_{fecha_fin_archivo}.pdf"
            
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            import traceback
            error_msg = f"ERROR generando PDF: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            return Response(
                {'error': error_msg},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def obtener_datos_reporte_directo(self, fecha_inicio, fecha_fin, proveedor_id):
        """
        Obtiene los datos del reporte calculando directamente
        """
        try:
            # Validar fechas
            fecha_inicio_dt = None
            fecha_fin_dt = None
            
            if fecha_inicio:
                try:
                    fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                except ValueError:
                    print(f"ERROR: Formato de fecha_inicio inválido: {fecha_inicio}")
                    fecha_inicio_dt = None
            
            if fecha_fin:
                try:
                    fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                except ValueError:
                    print(f"ERROR: Formato de fecha_fin inválido: {fecha_fin}")
                    fecha_fin_dt = None
            
            # Si solo una fecha está especificada, usar rango por defecto
            if fecha_inicio_dt and not fecha_fin_dt:
                fecha_fin_dt = fecha_inicio_dt + timedelta(days=30)
            elif fecha_fin_dt and not fecha_inicio_dt:
                fecha_inicio_dt = fecha_fin_dt - timedelta(days=30)
            
            print(f"DEBUG PDF - Fechas procesadas: {fecha_inicio_dt} a {fecha_fin_dt}")
            
            # Filtrar insumos activos
            insumos = Insumo.objects.filter(activo=True)
            
            # Aplicar filtro por proveedor
            if proveedor_id:
                insumos = insumos.filter(proveedor_id=proveedor_id)
                print(f"DEBUG PDF - Filtrado por proveedor_id: {proveedor_id}")
            
            print(f"DEBUG PDF - Total de insumos activos encontrados: {insumos.count()}")
            
            reporte_data = []
            
            # Usar métodos de ReporteInsumosAPIView para calcular stock usado
            reporte_view = ReporteInsumosAPIView()
            
            for insumo in insumos:
                try:
                    # Calcular stock usado desde recetas
                    stock_usado_recetas = reporte_view.calcular_stock_usado_recetas(
                        insumo, fecha_inicio_dt, fecha_fin_dt
                    )
                    
                    # Calcular stock usado desde ingredientes extra
                    stock_usado_ingredientes_extra = reporte_view.calcular_stock_usado_ingredientes_extra(
                        insumo, fecha_inicio_dt, fecha_fin_dt
                    )
                    
                    # Stock total usado
                    stock_usado_total = stock_usado_recetas + stock_usado_ingredientes_extra
                    
                    # Debug por insumo
                    if stock_usado_total > 0:
                        print(f"  ✓ {insumo.nombre}: stock_usado = {stock_usado_total}")
                    else:
                        print(f"  ✗ {insumo.nombre}: stock_usado = 0")
                    
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
                    
                except Exception as e:
                    print(f"ERROR procesando insumo {insumo.id} ({insumo.nombre}): {str(e)}")
                    # Agregar igual pero con stock usado 0 en caso de error
                    reporte_data.append({
                        'id': insumo.id,
                        'nombre': insumo.nombre,
                        'categoria': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                        'stock_usado': 0.0,
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
            
            return reporte_data
            
        except Exception as e:
            import traceback
            print(f"ERROR en obtener_datos_reporte_directo: {str(e)}")
            print(traceback.format_exc())
            return []
        
    def formatear_fecha_dd_mm_yyyy(self, fecha_str):
        """
        Convierte fecha de formato YYYY-MM-DD a DD/MM/YYYY
        """
        try:
            if isinstance(fecha_str, str):
                # Intentar parsear como YYYY-MM-DD
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
                return fecha_obj.strftime('%d/%m/%Y')
            elif hasattr(fecha_str, 'strftime'):  # Si ya es objeto datetime/date
                return fecha_str.strftime('%d/%m/%Y')
            else:
                return str(fecha_str)  # Devolver como está si no se puede convertir
        except (ValueError, AttributeError):
            # Si hay error, devolver la fecha original
            return str(fecha_str)
        
class GenerarPDFListaComprasAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Obtener parámetros de filtro
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            proveedor_id = request.GET.get('proveedor_id')
            
            # Obtener datos de lista de compras usando la misma lógica que ListaComprasAPIView
            lista_compras_view = ListaComprasAPIView()
            response = lista_compras_view.get(request)
            
            if response.status_code != 200:
                return response
            
            lista_compras_data = response.data
            
            # Filtrar solo los que necesitan compra
            items_comprar = [item for item in lista_compras_data if item['necesita_compra']]
            
            # Crear el PDF
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1,
                textColor=colors.HexColor('#7B5A50')
            )
            
            # Título - CON FORMATO DD/MM/YYYY
            title_text = "Lista de Compras - Próxima Semana"
            if fecha_inicio and fecha_fin:
                # Formatear fechas a DD/MM/YYYY
                fecha_inicio_fmt = self.formatear_fecha_dd_mm_yyyy(fecha_inicio)
                fecha_fin_fmt = self.formatear_fecha_dd_mm_yyyy(fecha_fin)
                title_text += f" - Del {fecha_inicio_fmt} al {fecha_fin_fmt}"
            
            elements.append(Paragraph(title_text, title_style))
            elements.append(Spacer(1, 20))
            
            # Preparar datos para la tabla - SIN DÍA COMPRA
            table_data = [['Insumo', 'Stock Actual', 'Stock Mínimo', 'Pedidos', 'Compra Sugerida', 'Proveedor']]
            
            for item in items_comprar:
                table_data.append([
                    f"{item['nombre']} ({item['categoria']})",
                    f"{item['stock_actual']:.3f} {item['unidad_medida']['abreviatura']}",
                    f"{item['stock_minimo']:.3f} {item['unidad_medida']['abreviatura']}",
                    f"{item['pedidos']:.3f} {item['unidad_medida']['abreviatura']}",
                    f"{item['total_comprar']:.3f} {item['unidad_medida']['abreviatura']}",
                    item['proveedor']['nombre'] if item['proveedor'] else 'Sin proveedor'
                ])
            
            # Crear tabla - AJUSTAR ANCHOS DE COLUMNAS SIN DÍA COMPRA
            table = Table(table_data, colWidths=[2.2*inch, 1*inch, 1*inch, 1*inch, 1.2*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#d4edda')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(table)
            
            # Agregar resumen
            elements.append(Spacer(1, 20))
            total_insumos = len(items_comprar)
            resumen_text = f"Total de insumos a comprar: {total_insumos}"
            resumen_style = ParagraphStyle(
                'Resumen',
                parent=styles['Normal'],
                fontSize=10,
                alignment=1,
                textColor=colors.HexColor('#28a745'),
                spaceBefore=10
            )
            elements.append(Paragraph(resumen_text, resumen_style))
            
            # Fecha de generación - FORMATO DD/MM/YYYY
            fecha_gen = ParagraphStyle(
                'FechaGen',
                parent=styles['Normal'],
                fontSize=9,
                alignment=1,
                textColor=colors.grey,
                spaceBefore=20
            )
            fecha_text = f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            elements.append(Paragraph(fecha_text, fecha_gen))
            
            # Construir PDF
            doc.build(elements)
            
            # Preparar respuesta
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            
            # Nombre del archivo
            filename = f"lista_compras_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            if fecha_inicio and fecha_fin:
                fecha_inicio_archivo = fecha_inicio.replace("-", "")
                fecha_fin_archivo = fecha_fin.replace("-", "")
                filename = f"lista_compras_{fecha_inicio_archivo}_a_{fecha_fin_archivo}.pdf"
            
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error al generar PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def formatear_fecha_dd_mm_yyyy(self, fecha_str):
        """
        Convierte fecha de formato YYYY-MM-DD a DD/MM/YYYY
        """
        try:
            if isinstance(fecha_str, str):
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
                return fecha_obj.strftime('%d/%m/%Y')
            elif hasattr(fecha_str, 'strftime'):
                return fecha_str.strftime('%d/%m/%Y')
            else:
                return str(fecha_str)
        except (ValueError, AttributeError):
            return str(fecha_str)