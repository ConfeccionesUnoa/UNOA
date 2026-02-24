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
    CorteListCreateAPIView,
    CorteRetrieveUpdateDestroyAPIView,
    PresentacionListCreateAPIView,
    PresentacionRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path('inventario/', InventarioListCreateAPIView.as_view(), name='core-inventario-api'),
    path('inventario/<uuid:uuid>/', InventarioRetrieveUpdateDestroyAPIView.as_view(), name='core-inventario-detail-api'),
    path('inventario/<uuid:uuid>/ingresos/', IngresoListCreateAPIView.as_view(), name='core-inventario-ingresos-api'),
    path('proveedor/', ProveedorListCreateAPIView.as_view(), name='core-proveedor-api'),
    path('proveedor/<uuid:uuid>/', ProveedorRetrieveUpdateDestroyAPIView.as_view(), name='core-proveedor-detail-api'),
    path('categoria/', CategoriaListCreateAPIView.as_view(), name='core-categoria-api'),
    path('categoria/<uuid:uuid>/', CategoriaRetrieveUpdateDestroyAPIView.as_view(), name='core-categoria-detail-api'),
    path('corte/', CorteListCreateAPIView.as_view(), name='core-corte-api'),
    path('corte/<uuid:uuid>/', CorteRetrieveUpdateDestroyAPIView.as_view(), name='core-corte-detail-api'),
    path('presentacion/', PresentacionListCreateAPIView.as_view(), name='core-presentacion-api'),
    path('presentacion/<uuid:uuid>/', PresentacionRetrieveUpdateDestroyAPIView.as_view(), name='core-presentacion-detail-api'),
    path('programacion/', ProgramacionListCreateAPIView.as_view(), name='core-programacion-api'),
    path('programacion/<uuid:uuid>/', ProgramacionListCreateAPIView.as_view(), name='core-programacion-detail-api'),
    path('programacion/<uuid:uuid>/insumos/', ProgramacionInsumoCreateAPIView.as_view(), name='core-programacion-insumos-api'),
]
