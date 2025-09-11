from django.db.models import F
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Insumo, UnidadMedida,CategoriaInsumo, Proveedor
from .serializers import InsumoSerializer, UnidadMedidaSerializer, CategoriaInsumoSerializer, ProveedorSerializer

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