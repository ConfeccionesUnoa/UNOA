from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status

from config.pagination import Paginacion
from .models import Inventario, IngresoInventario, Proveedor
from .serializers import (
    InventarioListRetrieveSerializer,
    InventarioCreateUpdateSerializer,
    IngresoInventarioListSerializer,
    IngresoInventarioCreateSerializer,
    ProveedorSerializer,
)
from config.mixins import ProtectedForeignKeyDeleteMixin


class InventarioListCreateAPIView(ListCreateAPIView):
    """
    Se encarga de listar y crear productos del inventario, soporta los métodos:
    GET y POST
    """
    queryset = Inventario.objects.all()
    serializer_class = InventarioListRetrieveSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('codigo', 'nombre', 'categoria', 'descripcion', 'observaciones', 'numero_factura', 'proveedor__nombre')
    ordering = ('-created',)
    pagination_class = Paginacion

    def get_serializer_class(self):
        if self.request and self.request.method == 'POST':
            return InventarioCreateUpdateSerializer
        return InventarioListRetrieveSerializer

    def get_queryset(self):
        return Inventario.objects.all()

    def perform_create(self, serializer):
        """Al crear un producto, si se provee cantidad > 0 o valor_ingreso, generamos un ingreso inicial.
        Evitamos doble conteo: guardamos el objeto con cantidad=0 y luego registramos el ingreso que actualizará la cantidad.
        """
        # Extraemos la cantidad indicada y guardamos el objeto con cantidad a 0 para evitar duplicación
        cantidad = serializer.validated_data.get('cantidad', 0)
        valor_ingreso = serializer.validated_data.get('valor_ingreso', 0)
        numero_factura = serializer.validated_data.get('numero_factura')
        fecha = serializer.validated_data.get('fecha')
        proveedor = serializer.validated_data.get('proveedor')
        observaciones = serializer.validated_data.get('observaciones')

        # Forzar cantidad inicial a 0 antes de crear el objeto
        instance_data = {**{k: v for k, v in serializer.validated_data.items() if k != 'cantidad'}}
        obj = serializer.create(instance_data)

        if cantidad and cantidad > 0:
            obj.agregar_ingreso(
                cantidad=cantidad,
                fecha=fecha,
                numero_factura=numero_factura,
                valor_ingreso=valor_ingreso,
                proveedor=proveedor,
                observaciones=observaciones,
            )


class InventarioRetrieveUpdateDestroyAPIView(ProtectedForeignKeyDeleteMixin, RetrieveUpdateDestroyAPIView):
    """
    Se encarga de visualizar, editar y borrar productos del inventario, soporta los métodos:
    GET, PUT y DELETE
    """
    queryset = Inventario.objects.all()
    serializer_class = InventarioListRetrieveSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request and self.request.method == 'PUT':
            return InventarioCreateUpdateSerializer
        return InventarioListRetrieveSerializer

    def get_queryset(self):
        return Inventario.objects.all()


class IngresoListCreateAPIView(ListCreateAPIView):
    """Listar y crear ingresos para un inventario específico"""
    serializer_class = IngresoInventarioListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        uuid = self.kwargs.get('uuid')
        return IngresoInventario.objects.filter(inventario__uuid=uuid)

    def post(self, request, *args, **kwargs):
        # Crear ingreso asociado al inventario y actualizar cantidad
        uuid = self.kwargs.get('uuid')
        try:
            inventario = Inventario.objects.get(uuid=uuid)
        except Inventario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = IngresoInventarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        ingreso = inventario.agregar_ingreso(
            cantidad=data.get('cantidad'),
            fecha=data.get('fecha'),
            numero_factura=data.get('numero_factura'),
            valor_ingreso=data.get('valor_ingreso', 0),
            proveedor=data.get('proveedor'),
            observaciones=data.get('observaciones')
        )

        output_serializer = IngresoInventarioListSerializer(ingreso)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class ProveedorListCreateAPIView(ListCreateAPIView):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = (IsAuthenticated,)
