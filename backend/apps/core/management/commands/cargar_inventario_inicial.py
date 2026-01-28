from django.core.management.base import BaseCommand
from apps.core.models import Inventario


class Command(BaseCommand):
    help = 'Carga datos iniciales en el inventario'

    def handle(self, *args, **options):
        # Datos de ejemplo para el inventario
        productos = [
            {
                'codigo': 'BOB-001',
                'nombre': 'Bobina de Cobre 1kg',
                'descripcion': 'Bobina de cobre de alta calidad para aplicaciones industriales',
                'cantidad': 150,
                'precio_unitario': 25000.00,
                'categoria': 'Materiales Básicos',
                'estado': 'AC'
            },
            {
                'codigo': 'BOB-002',
                'nombre': 'Bobina de Aluminio 500g',
                'descripcion': 'Bobina de aluminio ligera para proyectos especiales',
                'cantidad': 200,
                'precio_unitario': 15000.00,
                'categoria': 'Materiales Básicos',
                'estado': 'AC'
            },
            {
                'codigo': 'BOB-003',
                'nombre': 'Alambre Esmaltado 0.5mm',
                'descripcion': 'Alambre esmaltado para transformadores',
                'cantidad': 500,
                'precio_unitario': 8000.00,
                'categoria': 'Conductores',
                'estado': 'AC'
            },
            {
                'codigo': 'BOB-004',
                'nombre': 'Aislante Papel Kraft',
                'descripcion': 'Papel kraft para aislamiento de bobinas',
                'cantidad': 1000,
                'precio_unitario': 5000.00,
                'categoria': 'Aislantes',
                'estado': 'AC'
            },
            {
                'codigo': 'BOB-005',
                'nombre': 'Núcleo de Hierro Laminado',
                'descripcion': 'Núcleo de hierro laminado para transformadores',
                'cantidad': 75,
                'precio_unitario': 45000.00,
                'categoria': 'Núcleos',
                'estado': 'AC'
            },
            {
                'codigo': 'BOB-006',
                'nombre': 'Soldadura de Estaño',
                'descripcion': 'Soldadura de estaño de alta pureza',
                'cantidad': 100,
                'precio_unitario': 12000.00,
                'categoria': 'Accesorios',
                'estado': 'AC'
            },
            {
                'codigo': 'BOB-007',
                'nombre': 'Caja de Protección Plástica',
                'descripcion': 'Caja de protección resistente para bobinados',
                'cantidad': 250,
                'precio_unitario': 3500.00,
                'categoria': 'Protección',
                'estado': 'AC'
            },
            {
                'codigo': 'BOB-008',
                'nombre': 'Tornillos de Sujeción M6',
                'descripcion': 'Tornillos acero inoxidable para sujeción de bobinas',
                'cantidad': 2000,
                'precio_unitario': 500.00,
                'categoria': 'Accesorios',
                'estado': 'AC'
            },
            {
                'codigo': 'BOB-009',
                'nombre': 'Adhesivo Epoxídico',
                'descripcion': 'Adhesivo epoxídico de dos componentes',
                'cantidad': 50,
                'precio_unitario': 18000.00,
                'categoria': 'Químicos',
                'estado': 'AC'
            },
            {
                'codigo': 'BOB-010',
                'nombre': 'Tubo de PVC 1 pulgada',
                'descripcion': 'Tubo de PVC para protección de conductores',
                'cantidad': 150,
                'precio_unitario': 2500.00,
                'categoria': 'Protección',
                'estado': 'AC'
            },
        ]

        for producto in productos:
            # Verifica si el producto ya existe para no duplicar
            if not Inventario.objects.filter(codigo=producto['codigo']).exists():
                Inventario.objects.create(**producto)
                self.stdout.write(self.style.SUCCESS(f"✓ Producto {producto['codigo']} creado exitosamente"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠ Producto {producto['codigo']} ya existe"))

        self.stdout.write(self.style.SUCCESS('\n¡Datos iniciales cargados correctamente!'))
