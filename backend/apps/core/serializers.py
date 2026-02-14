from rest_framework import serializers
from .models import Inventario, IngresoInventario, Proveedor, Programacion, ProgramacionInsumo, Categoria, Corte, CorteDetalle


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


class CorteDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorteDetalle
        fields = ['uuid', 'numero', 'proporcion', 'unidades_cortadas', 'ancho', 'largo', 'promedio', 'mtrs_consumidos', 'color', 'created']
        read_only_fields = ['uuid', 'created']


class CorteSerializer(serializers.ModelSerializer):
    detalles = CorteDetalleSerializer(many=True, read_only=True)
    detalles_input = CorteDetalleSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Corte
        fields = [
            'uuid', 'tercero', 'fecha', 'ref', 'tela', 'mtrs_enviados', 'lote', 'orden_produccion', 'notas', 'tallas',
            'total_unidades', 'total_metros_consumidos', 'mtrs_retazos', 'promedio', 'muestras', 'faltante_tela',
            'consumo_cantidad', 'consumo_metros_gastados', 'consumo_ancho', 'consumo_largo', 'consumo_promedio', 'sobrante_tela', 'firma_responsable',
            'detalles', 'detalles_input', 'created'
        ]
        read_only_fields = ['uuid', 'created', 'detalles']

    def create(self, validated_data):
        detalles_input = validated_data.pop('detalles_input', [])
        corte = Corte.objects.create(**validated_data)
        for d in detalles_input:
            CorteDetalle.objects.create(corte=corte, **d)
        return corte

    def update(self, instance, validated_data):
        detalles_input = validated_data.pop('detalles_input', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if detalles_input is not None:
            # replace detalles
            instance.detalles.all().delete()
            for d in detalles_input:
                CorteDetalle.objects.create(corte=instance, **d)
        return instance


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
