from django.urls import path
from . import views

urlpatterns = [
    # Página principal → login
    path('', views.login_view, name='login'),
    #Inventario
    path('inventario/', views.inventario, name='inventario'),
    #Funciones Inventario
    path('inventario/agregar/', views.agregar_inventario, name='agregar_inventario'),
    path('inventario/editar/<int:id>/', views.editar_inventario, name='editar_inventario'),
    path('inventario/eliminar/<int:id>/', views.eliminar_inventario, name='eliminar_inventario'),

    #Unidades De Medida
    path('unidad-medida/', views.unidad_medida, name='unidad_medida'),
    #Funciones Unidades De Medida
    path('unidad-medida/agregar/', views.agregar_unidad_medida, name='agregar_unidad_medida'),
    path('unidad-medida/editar/<int:id>/', views.editar_unidad_medida, name='editar_unidad_medida'),
    path('unidad-medida/eliminar/<int:id>/', views.eliminar_unidad_medida, name='eliminar_unidad_medida'),
    #Categorias
    path('categoria/', views.categoria, name='categoria'),
    #Funciones Categorias
    path('categoria/agregar/', views.agregar_categoria, name='agregar_categoria'),
    path('categoria/editar/<int:id>/', views.editar_categoria, name='editar_categoria'),
    path('categoria/eliminar/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),
    #Caducidad
    path('caducidad/', views.caducidad, name='caducidad'),
    # Funciones Lotes de Producto
    path('caducidad/agregar/', views.agregar_lote, name='agregar_lote'),
    path('caducidad/editar/<int:id>/', views.editar_lote, name='editar_lote'),
    path('caducidad/eliminar/<int:id>/', views.eliminar_lote, name='eliminar_lote'),
    #StockBajo
    path('stock-bajo/', views.stock_bajo, name='stock_bajo'),
    #Proveedores
    path('proveedores/', views.proveedores, name='proveedores'),
    #Funciones Proveedores
    path('proveedores/agregar', views.agregar_proveedor, name='agregar_proveedor'),
    path('proveedores/editar/<int:id>/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/eliminar/<int:id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    #Empleados
    #Personal
    path('personal/', views.personal_list, name='personal'),
    #Funciones Personal
    path('personal/agregar/', views.agregar_personal, name='agregar_personal'),
    path('personal/editar/<int:id>/', views.editar_personal, name='editar_personal'),
    path('personal/eliminar/<int:id>/', views.eliminar_personal, name='eliminar_personal'),

    #Cuentas
    path('cuentas/', views.cuenta_list, name='cuentas'),
    #Funciones Cuentas
    path('cuentas/agregar/', views.agregar_cuenta, name='agregar_cuenta'),
    path('cuentas/editar/<int:id>/', views.editar_cuenta, name='editar_cuenta'),
    path('cuentas/eliminar/<int:id>/', views.eliminar_cuenta, name='eliminar_cuenta'),
    #Clientes
    path('clientes/', views.clientes, name='clientes'),
    #Funciones Clientes
    path('clientes/agregar/', views.agregar_cliente, name='agregar_cliente'),
    path('clientes/editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),

    # Compras
    # Pantalla principal (sidebar)
    path('compras/registro/', views.registro_compra, name='registro_compra'),
    # Funciones sobre la tabla local (no BD)
    path('compras/agregar/', views.agregar_compra_local, name='agregar_compra'),
    path('compras/editar/<int:id>/', views.editar_compra_local, name='editar_compra'),
    path('compras/eliminar/<int:id>/', views.eliminar_compra_local, name='eliminar_compra'),
    # Registrar en BD (cuando ya está lista la tabla local)
    path('compras/registrar/', views.registrar_compra, name='registrar_compra'),
    #Devuelve las Unidades
    path('compras/unidades/<int:producto_id>/', views.unidades_por_producto, name='unidades_por_producto'),
    #Cancelar Compra
    path('compras/cancelar/', views.cancelar_compra, name='cancelar_compra'),
    # Consulta de compras (historial general en BD)
    path('compras/consulta/', views.consulta_compras, name='consulta_compras'),
    path('compras/reporte/<int:id_compra>/', views.reporte_compra_pdf, name='reporte_compra_pdf'),

    #Ventas
    # Pantalla principal (caja)
    path('ventas/caja/', views.caja, name='caja'),
    # Funciones sobre la tabla local (no BD)
    path('ventas/agregar/', views.agregar_venta_local, name='agregar_venta'),
    path('ventas/editar/<int:id>/', views.editar_venta_local, name='editar_venta'),
    path('ventas/eliminar/<int:id>/', views.eliminar_venta_local, name='eliminar_venta'),
    # Registrar en BD (cuando ya está lista la tabla local)
    path('ventas/registrar/', views.registrar_venta, name='registrar_venta'),
    # Devuelve las Unidades (según producto)
    path('ventas/unidades/<int:producto_id>/', views.unidades_por_producto_venta, name='unidades_por_producto_venta'),
    # Devuelve los lotes (según producto)
    path('ventas/lotes/<int:producto_id>/', views.lotes_por_producto, name='lotes_por_producto'),
    # Cancelar Venta
    path('ventas/cancelar/', views.cancelar_venta, name='cancelar_venta'),
    # Historial de ventas
    path('ventas/historial/', views.historial_ventas, name='historial_ventas'),
    # Reporte de venta en PDF
    path('ventas/reporte/<int:id_venta>/', views.reporte_venta_pdf, name='reporte_venta_pdf'),

    #Login y Logout
    path('login/', views.login_view, name='login'),
    path('inicio/', views.inicio, name='inicio'),
    path('logout/', views.logout_view, name='logout'),

]
