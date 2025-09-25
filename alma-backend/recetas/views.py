from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from decimal import Decimal

# Importar los modelos correctamente
from .models import Receta, RecetaInsumo
from .serializers import RecetaSerializer, RecetaInsumoSerializer, RecetaInsumoCreateSerializer
from insumos.models import Insumo
from insumos.conversiones import convertir_unidad


class RecetaListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Receta.objects.all().order_by('-creado_en')
    serializer_class = RecetaSerializer

    def perform_create(self, serializer):
        print("Datos recibidos:", self.request.data)
        serializer.save()


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


# -------------------------
# 🔹 Incrementar Receta
# -------------------------
class IncrementarRecetaView(APIView):
    def post(self, request, pk):
        try:
            with transaction.atomic():
                receta = Receta.objects.get(pk=pk)
                detalles = RecetaInsumo.objects.filter(receta=receta)

                # Verificar stock antes de incrementar
                insuficientes = []
                for detalle in detalles:
                    # DEBUG: Verificar si el método existe
                    if not hasattr(detalle, 'get_cantidad_en_unidad_insumo'):
                        return Response({
                            'error': f'Método no encontrado en objeto tipo {type(detalle)}'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                    # Intentar llamar al método
                    try:
                        cantidad_necesaria = detalle.get_cantidad_en_unidad_insumo()
                    except AttributeError as e:
                        return Response({
                            'error': f'Error al llamar método: {str(e)}'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                    if not isinstance(cantidad_necesaria, Decimal):
                        cantidad_necesaria = Decimal(str(cantidad_necesaria))

                    stock_actual = detalle.insumo.stock_actual
                    if not isinstance(stock_actual, Decimal):
                        stock_actual = Decimal(str(stock_actual))

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

                # Reducir stock (usando cantidad directa temporalmente)
                for detalle in detalles:
                    # Usar cantidad directa en lugar del método problemático
                    cantidad_necesaria = detalle.cantidad
                    if not isinstance(cantidad_necesaria, Decimal):
                        cantidad_necesaria = Decimal(str(cantidad_necesaria))
                    
                    if not isinstance(detalle.insumo.stock_actual, Decimal):
                        detalle.insumo.stock_actual = Decimal(str(detalle.insumo.stock_actual))
                    
                    detalle.insumo.stock_actual -= cantidad_necesaria
                    detalle.insumo.save()

                receta.veces_hecha += 1
                receta.save()

                return Response({
                    'nuevo_contador': receta.veces_hecha,
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
                if receta.veces_hecha <= 0:
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

                receta.veces_hecha -= 1
                receta.save()

                return Response({
                    'nuevo_contador': receta.veces_hecha,
                    'stock_actualizado': True,
                    'mensaje': f'Se ha revertido la preparación de "{receta.nombre}"',
                    'insumos_devueltos': insumos_devueltos
                }, status=status.HTTP_200_OK)

        except Receta.DoesNotExist:
            return Response({'error': 'Receta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Error interno del servidor: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)