# views.py - Versión COMPLETA y corregida
from django.db.models import F
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse, JsonResponse
from .models import Insumo, UnidadMedida, CategoriaInsumo, Proveedor
from .serializers import InsumoSerializer, UnidadMedidaSerializer, CategoriaInsumoSerializer, ProveedorSerializer
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Q
from django.db import models
from datetime import datetime, timedelta, date
from decimal import Decimal
import io
from django.utils import timezone

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
        if Insumo.objects.filter(nombre__iexact=nombre).exists():
            return Response(
                {'error': 'Ya existe un insumo con este nombre'},
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

# ==================== VISTAS PARA REPORTES ====================
class ReporteInsumosAPIView(APIView):
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
                
                # Calcular cantidad total a comprar
                # (Stock mínimo - Stock actual) + Pedidos del período
                stock_minimo = insumo.stock_minimo
                stock_actual = insumo.stock_actual
                total_comprar = max(Decimal('0.0'), (stock_minimo - stock_actual) + pedidos_periodo)
                
                # Determinar día de compra según el proveedor
                dia_compra = self.determinar_dia_compra(insumo.proveedor)
                
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
                    'dia_compra': dia_compra,
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
    
    def determinar_dia_compra(self, proveedor):
        """
        Determina el día de compra según el proveedor
        """
        if not proveedor:
            return "Sin asignar"
        
        proveedor_nombre = proveedor.nombre.lower()
        
        # Lunes - Verdulería: frutas y verduras
        if any(palabra in proveedor_nombre for palabra in ['verduleria', 'fruta', 'verdura', 'fruteria']):
            return "Lunes"
        
        # Martes - Tregar: crema, manteca, yogures
        elif 'tregar' in proveedor_nombre:
            return "Martes"
        
        # Jueves - La Serenísima: leche entera, leche de almendras, ricota, crema, queso Finlandia
        elif any(palabra in proveedor_nombre for palabra in ['serenisima', 'lacteo', 'leche', 'lácteo', 'queso', 'ricota', 'crema']):
            return "Jueves"
        
        # Viernes - Alcom: chocolate, harina, azúcar, garbanzos, granola
        elif any(palabra in proveedor_nombre for palabra in ['alcom', 'almacen', 'harina', 'azucar', 'azúcar', 'chocolate', 'garbanzo', 'granola']):
            return "Viernes"
        
        else:
            return "Sin asignar"

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
            
            # Determinar día de compra
            dia_compra = "Sin asignar"
            if insumo.proveedor:
                proveedor_nombre = insumo.proveedor.nombre.lower()
                if any(palabra in proveedor_nombre for palabra in ['verduleria', 'fruta', 'verdura']):
                    dia_compra = "Lunes"
                elif 'tregar' in proveedor_nombre:
                    dia_compra = "Martes"
                elif any(palabra in proveedor_nombre for palabra in ['serenisima', 'lacteo', 'leche']):
                    dia_compra = "Jueves"
                elif any(palabra in proveedor_nombre for palabra in ['alcom', 'almacen', 'harina', 'azucar']):
                    dia_compra = "Viernes"
            
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
                'dia_compra': dia_compra,
                'necesita_compra': total_comprar > 0
            })
        
        return JsonResponse(lista_compras_data, safe=False)
        
    except Exception as e:
        return JsonResponse(
            {'error': f'Error al generar lista de compras: {str(e)}'},
            status=500
        )