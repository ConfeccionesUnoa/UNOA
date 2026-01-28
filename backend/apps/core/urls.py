from django.urls import path

from .views import (
    InventarioListCreateAPIView,
    InventarioRetrieveUpdateDestroyAPIView,
    IngresoListCreateAPIView,
    ProveedorListCreateAPIView,
)

urlpatterns = [
    path('inventario/', InventarioListCreateAPIView.as_view(), name='core-inventario-api'),
    path('inventario/<uuid:uuid>/', InventarioRetrieveUpdateDestroyAPIView.as_view(), name='core-inventario-detail-api'),
    path('inventario/<uuid:uuid>/ingresos/', IngresoListCreateAPIView.as_view(), name='core-inventario-ingresos-api'),
    path('proveedor/', ProveedorListCreateAPIView.as_view(), name='core-proveedor-api'),
]
