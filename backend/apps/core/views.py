from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status

from config.pagination import Paginacion
from .models import Inventario, IngresoInventario, Proveedor, Programacion, ProgramacionInsumo, Categoria, Corte, Presentacion, Cliente, Lavanderia
from .serializers import (
    InventarioListRetrieveSerializer,
    InventarioCreateUpdateSerializer,
    IngresoInventarioListSerializer,
    IngresoInventarioCreateSerializer,
    ProveedorSerializer,
    CategoriaSerializer,
    ClienteSerializer,
    CorteSerializer,
    ProgramacionSerializer,
    ProgramacionInsumoSerializer,
    PresentacionSerializer,
    LavanderiaSerializer,
)
from .models import Presentacion
from .serializers import PresentacionSerializer
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


class ProveedorRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)


class CategoriaListCreateAPIView(ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = (IsAuthenticated,)


class CategoriaRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)


class ClienteListCreateAPIView(ListCreateAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = (IsAuthenticated,)


class ClienteRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)


class ProgramacionListCreateAPIView(ListCreateAPIView):
    """Listar y crear programaciones (órdenes)"""
    queryset = Programacion.objects.all()
    serializer_class = ProgramacionSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('numero_orden', 'codigo', 'descripcion', 'proveedor__nombre')

    def get_queryset(self):
        # Excluir programaciones que están "finalizadas" (todos los cortes en TERMINADO)
        from apps.core.models import Corte
        programaciones_finalizadas = Corte.objects.filter(
            estado=Corte.ESTADO_TERMINADO
        ).values_list('orden_produccion', flat=True).distinct()
        
        # Obtener programaciones que NO están en la lista de finalizadas
        return Programacion.objects.exclude(numero_orden__in=programaciones_finalizadas)


class ProgramacionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """Obtener, actualizar y eliminar programaciones individuales"""
    queryset = Programacion.objects.all()
    serializer_class = ProgramacionSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'

    def get_object(self):
        # Intentamos primero buscar por UUID, luego por PK si no existe.
        lookup_val = self.kwargs.get('uuid') or self.kwargs.get('pk')

        if not lookup_val:
            raise Http404

        # Primero por uuid
        try:
            return Programacion.objects.get(uuid=lookup_val)
        except (Programacion.DoesNotExist, ValueError):
            pass

        # Segundo por pk
        try:
            return Programacion.objects.get(pk=lookup_val)
        except (Programacion.DoesNotExist, ValueError):
            raise Http404


class ProgramacionInsumoCreateAPIView(ListCreateAPIView):
    """Listar insumos de una programacion y crear solicitudes de insumos que afecten inventario"""
    serializer_class = ProgramacionInsumoSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        uuid = self.kwargs.get('uuid')
        return ProgramacionInsumo.objects.filter(programacion__uuid=uuid)

    def post(self, request, *args, **kwargs):
        # Esperamos un payload con lista de insumos: [{ 'inventario': '<uuid>', 'cantidad': 1 }, ...]
        uuid = self.kwargs.get('uuid')
        try:
            programacion = Programacion.objects.get(uuid=uuid)
        except Programacion.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        items = request.data.get('items') if isinstance(request.data, dict) else request.data
        if not items:
            return Response({'detail': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)

        created_items = []
        from django.db import transaction
        try:
            with transaction.atomic():
                for it in items:
                    inv_uuid = it.get('inventario') or it.get('inventario_uuid')
                    cantidad = int(it.get('cantidad') or 0)
                    if not inv_uuid or cantidad <= 0:
                        raise ValueError('inventario and cantidad required')

                    inventario = Inventario.objects.select_for_update().get(uuid=inv_uuid)
                    if inventario.cantidad < cantidad:
                        raise ValueError(f'Inventario insuficiente para {inventario.codigo}')

                    # Restar del inventario
                    inventario.cantidad = inventario.cantidad - cantidad
                    inventario.save()

                    # Crear registro de ProgramacionInsumo
                    pi = ProgramacionInsumo.objects.create(
                        programacion=programacion,
                        inventario=inventario,
                        cantidad=cantidad
                    )
                    created_items.append(pi)
        except Inventario.DoesNotExist:
            return Response({'detail': 'Inventario not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        output = ProgramacionInsumoSerializer(created_items, many=True)
        return Response(output.data, status=status.HTTP_201_CREATED)


class CorteListCreateAPIView(ListCreateAPIView):
    queryset = None
    serializer_class = None
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Corte.objects.all()

    def get_serializer_class(self):
        return CorteSerializer


class CorteRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Corte.objects.all()
    serializer_class = CorteSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)


class PresentacionListCreateAPIView(ListCreateAPIView):
    queryset = None
    serializer_class = None
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Presentacion.objects.all()

    def get_serializer_class(self):
        return PresentacionSerializer


class PresentacionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Presentacion.objects.all()
    serializer_class = PresentacionSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)


class LavanderiaListCreateAPIView(ListCreateAPIView):
    queryset = None
    serializer_class = None
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Lavanderia.objects.all()

    def get_serializer_class(self):
        return LavanderiaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            print("Errores de validación en Lavanderia:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LavanderiaRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Lavanderia.objects.all()
    serializer_class = LavanderiaSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)
