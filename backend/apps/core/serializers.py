from rest_framework import serializers
from .models import Inventario, IngresoInventario, Proveedor, Programacion, ProgramacionInsumo, Categoria


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['uuid', 'nombre']
        read_only_fields = ['uuid']


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['uuid', 'nombre']
        read_only_fields = ['uuid']


class IngresoInventarioListSerializer(serializers.ModelSerializer):
    proveedor = ProveedorSerializer(read_only=True)

    class Meta:
        model = IngresoInventario
        fields = ['uuid', 'inventario', 'cantidad', 'fecha', 'numero_factura', 'valor_ingreso', 'proveedor', 'observaciones', 'created']
        read_only_fields = ['uuid', 'created']


class IngresoInventarioCreateSerializer(serializers.ModelSerializer):
    proveedor = serializers.SlugRelatedField(queryset=Proveedor.objects.all(), slug_field='uuid', allow_null=True, required=False)

    class Meta:
        model = IngresoInventario
        fields = ['uuid', 'cantidad', 'fecha', 'numero_factura', 'valor_ingreso', 'proveedor', 'observaciones']
        read_only_fields = ['uuid']


class InventarioListRetrieveSerializer(serializers.ModelSerializer):
    valor_total = serializers.SerializerMethodField()
    proveedor = ProveedorSerializer(read_only=True)

    class Meta:
        model = Inventario
        fields = ['uuid', 'codigo', 'nombre', 'descripcion', 'observaciones', 'proveedor', 'cantidad', 'valor_ingreso', 'numero_factura', 'fecha', 'precio_unitario', 'valor_total', 'categoria', 'estado', 'created', 'modified']
        read_only_fields = ['uuid', 'valor_total', 'created', 'modified']

    def get_valor_total(self, obj):
        return float(obj.valor_total)


class InventarioCreateUpdateSerializer(serializers.ModelSerializer):
    proveedor = serializers.SlugRelatedField(queryset=Proveedor.objects.all(), slug_field='uuid', allow_null=True, required=False)

    class Meta:
        model = Inventario
        fields = ['uuid', 'codigo', 'nombre', 'descripcion', 'observaciones', 'proveedor', 'cantidad', 'valor_ingreso', 'numero_factura', 'fecha', 'precio_unitario', 'categoria', 'estado']
        read_only_fields = ['uuid']


class ProgramacionInsumoSerializer(serializers.ModelSerializer):
    inventario = InventarioListRetrieveSerializer(read_only=True)
    inventario_uuid = serializers.SlugRelatedField(queryset=Inventario.objects.all(), slug_field='uuid', write_only=True, source='inventario')

    class Meta:
        model = ProgramacionInsumo
        fields = ['uuid', 'programacion', 'inventario', 'inventario_uuid', 'cantidad', 'created']
        read_only_fields = ['uuid', 'created', 'inventario']


class ProgramacionSerializer(serializers.ModelSerializer):
    proveedor = ProveedorSerializer(read_only=True)
    proveedor_uuid = serializers.SlugRelatedField(queryset=Proveedor.objects.all(), slug_field='uuid', write_only=True, source='proveedor', allow_null=True, required=False)
    insumos = ProgramacionInsumoSerializer(many=True, read_only=True)

    class Meta:
        model = Programacion
        fields = ['uuid', 'numero_orden', 'codigo', 'descripcion', 'proveedor', 'proveedor_uuid', 'insumos', 'created']
        read_only_fields = ['uuid', 'created', 'insumos']
