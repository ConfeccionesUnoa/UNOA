from rest_framework import serializers
from django.db.models import Sum
from .models import Inventario, IngresoInventario, Proveedor, Programacion, ProgramacionInsumo, Categoria, Corte, CorteDetalle, Presentacion, Cliente, Lavanderia


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


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
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
            'uuid', 'tercero', 'fecha', 'tela', 'mtrs_enviados', 'lote', 'orden_produccion', 'notas', 'tallas',
            'total_unidades', 'total_metros_consumidos', 'mtrs_retazos', 'promedio', 'muestras', 'faltante_tela',
            'consumo_cantidad', 'consumo_metros_gastados', 'consumo_ancho', 'consumo_largo', 'consumo_promedio', 'sobrante_tela', 'firma_responsable',
            'estado', 'fecha_estado',
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
    cliente = ClienteSerializer(read_only=True)
    cliente_uuid = serializers.SlugRelatedField(queryset=Cliente.objects.all(), slug_field='uuid', write_only=True, source='cliente', allow_null=True, required=False)
    insumos = ProgramacionInsumoSerializer(many=True, read_only=True)

    class Meta:
        model = Programacion
        fields = ['uuid', 'numero_orden', 'codigo', 'descripcion', 'proveedor', 'proveedor_uuid', 'cliente', 'cliente_uuid', 'fecha_entrega', 'tallas', 'prioridad', 'insumos', 'created']
        read_only_fields = ['uuid', 'created', 'insumos']


class LavanderiaSerializer(serializers.ModelSerializer):
    programacion = ProgramacionSerializer(read_only=True)
    programacion_uuid = serializers.SlugRelatedField(queryset=Programacion.objects.all(), slug_field='uuid', source='programacion', write_only=True, allow_null=True, required=False)
    corte = CorteSerializer(read_only=True)
    remision_salida_data = serializers.SerializerMethodField(read_only=True)
    remision_salida_uuid = serializers.SlugRelatedField(queryset=Lavanderia.objects.filter(tipo=Lavanderia.TIPO_SALIDA), slug_field='uuid', source='remision_salida', write_only=True, allow_null=True, required=False)

    class Meta:
        model = Lavanderia
        fields = [
            'uuid', 'programacion', 'programacion_uuid', 'corte', 'remision_salida_data', 'remision_salida_uuid', 'referencia', 'fecha', 'numero_remision', 'lavanderia',
            'cantidad', 'tipo', 'cantidad_conformes', 'cantidad_no_conformes', 'created'
        ]
        read_only_fields = ['uuid', 'created']
        extra_kwargs = {
            'referencia': {'allow_blank': True},
        }

    def get_remision_salida_data(self, obj):
        if obj.remision_salida:
            return {
                'uuid': str(obj.remision_salida.uuid),
                'numero_remision': obj.remision_salida.numero_remision,
                'cantidad': obj.remision_salida.cantidad
            }
        return None

    def validate(self, attrs):
        if attrs.get('tipo') == Lavanderia.TIPO_RECEPCION:
            remision_salida = attrs.get('remision_salida')
            if not remision_salida:
                raise serializers.ValidationError("Para recepciones, debe seleccionar una remisión de salida.")
            # Validar cantidad no exceda pendiente
            cantidad = attrs.get('cantidad', 0)
            try:
                recepciones_previas = Lavanderia.objects.filter(remision_salida=remision_salida, tipo=Lavanderia.TIPO_RECEPCION).aggregate(total=Sum('cantidad'))['total'] or 0
                pendiente = remision_salida.cantidad - recepciones_previas
                if cantidad > pendiente:
                    raise serializers.ValidationError(f"La cantidad no puede exceder la pendiente ({pendiente}).")
            except Exception as e:
                raise serializers.ValidationError(f"Error validando remisión de salida: {str(e)}")
        return attrs


class PresentacionSerializer(serializers.ModelSerializer):
    cortes = CorteSerializer(many=True, read_only=True)
    cortes_input = serializers.SlugRelatedField(queryset=Corte.objects.all(), many=True, slug_field='uuid', write_only=True, required=False)
    programacion_uuid = serializers.SlugRelatedField(queryset=Programacion.objects.all(), slug_field='uuid', write_only=True, source='programacion', allow_null=True, required=False)

    class Meta:
        model = Presentacion
        fields = ['uuid', 'programacion', 'programacion_uuid', 'numero_orden', 'fecha', 'referencia', 'estado_proceso', 'fecha_finalizacion', 'cortes', 'cortes_input', 'created']
        read_only_fields = ['uuid', 'created', 'cortes']

    def create(self, validated_data):
        cortes_input = validated_data.pop('cortes_input', [])
        pres = Presentacion.objects.create(**validated_data)
        if cortes_input:
            pres.cortes.set(cortes_input)
        return pres

    def update(self, instance, validated_data):
        cortes_input = validated_data.pop('cortes_input', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if cortes_input is not None:
            instance.cortes.set(cortes_input)
        return instance
