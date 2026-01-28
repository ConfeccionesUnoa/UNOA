from rest_framework import serializers
from .models import Inventario, IngresoInventario, Proveedor


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
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
