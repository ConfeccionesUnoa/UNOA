from django.urls import path

from .views import (
    InventarioListCreateAPIView,
    InventarioRetrieveUpdateDestroyAPIView,
    IngresoListCreateAPIView,
    ProveedorListCreateAPIView,
    ProveedorRetrieveUpdateDestroyAPIView,
    CategoriaListCreateAPIView,
    CategoriaRetrieveUpdateDestroyAPIView,
    ProgramacionListCreateAPIView,
    ProgramacionInsumoCreateAPIView,
)

urlpatterns = [
    path('inventario/', InventarioListCreateAPIView.as_view(), name='core-inventario-api'),
    path('inventario/<uuid:uuid>/', InventarioRetrieveUpdateDestroyAPIView.as_view(), name='core-inventario-detail-api'),
    path('inventario/<uuid:uuid>/ingresos/', IngresoListCreateAPIView.as_view(), name='core-inventario-ingresos-api'),
    path('proveedor/', ProveedorListCreateAPIView.as_view(), name='core-proveedor-api'),
    path('proveedor/<uuid:uuid>/', ProveedorRetrieveUpdateDestroyAPIView.as_view(), name='core-proveedor-detail-api'),
    path('categoria/', CategoriaListCreateAPIView.as_view(), name='core-categoria-api'),
    path('categoria/<uuid:uuid>/', CategoriaRetrieveUpdateDestroyAPIView.as_view(), name='core-categoria-detail-api'),
    path('programacion/', ProgramacionListCreateAPIView.as_view(), name='core-programacion-api'),
    path('programacion/<uuid:uuid>/', ProgramacionListCreateAPIView.as_view(), name='core-programacion-detail-api'),
    path('programacion/<uuid:uuid>/insumos/', ProgramacionInsumoCreateAPIView.as_view(), name='core-programacion-insumos-api'),
]
