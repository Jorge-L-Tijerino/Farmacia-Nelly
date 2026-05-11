```mermaid
classDiagram
    class Personal {
        +Id_Empleado
        +Nombre_Empleado
        +Cedula_Empleado
        +Telefono_Empleado
        +DiasTrabajo
        +HoraEntrada
        +HoraSalida
        +Turno
        +registrarEmpleado()
        +editarEmpleado()
        +eliminarEmpleado()
        +asignarTurno()
    }

    class Cuenta {
        +Id_Usuario
        +Rol
        +Estado
        +Correo_Empleados
        +Pass
        +crearCuenta()
        +validarLogin()
        +cambiarEstado()
    }

    class Proveedor {
        +Id_Proveedor
        +Tipo_Proveedor
        +Nombre_Proveedor
        +Telefono_Proveedor
        +Correo_Proveedor
        +Direccion_Proveedor
        +DiaEntrega
        +HoraEntrega
        +Estado_Proveedor
        +registrarProveedor()
        +editarProveedor()
        +eliminarProveedor()
    }

    class Cliente {
        +Id_Cliente
        +Nombre_Cliente
        +registrarCliente()
        +editarCliente()
        +eliminarCliente()
    }

    class Inventario {
        +Id_Medicamento
        +Nombre_Medicamento
        +Descripcion
        +Stock
        +agregarProducto()
        +actualizarStock()
        +eliminarProducto()
    }

    class Categoria {
        +Id_Categoria
        +Nombre_Categoria
        +crearCategoria()
        +editarCategoria()
        +eliminarCategoria()
    }

    class UnidadMedida {
        +Id_UnidadMedida
        +NombreUnidad
        +Equivalencia
        +Precio_Compra
        +Ganancia
        +Precio_Venta
        +calcularGanancia()
        +registrarUnidad()
        +editarUnidad()
    }

    class LotesProducto {
        +Id_Lote
        +FechaCaducidad
        +Cantidad
        +registrarLote()
        +editarLote()
        +verificarCaducidad()
    }

    class Compra {
        +Id_Compra
        +FechaCompra
        +Total
        +registrarCompra()
        +calcularTotal()
    }

    class DetalleCompra {
        +Id_DetalleCompra
        +Cantidad
        +Precio
        +FechaCaducidad
        +registrarDetalle()
        +calcularSubtotal()
    }

    class Venta {
        +Id_Venta
        +Fecha
        +MontoTotal
        +registrarVenta()
        +calcularTotal()
    }

    class DetalleVenta {
        +Id_DetalleVenta
        +Cantidad
        +Precio
        +registrarDetalle()
        +calcularSubtotal()
    }

    Personal "1" --> "N" Cuenta
    Personal "1" --> "N" Compra
    Personal "1" --> "N" Venta
    Proveedor "1" --> "N" Inventario
    Proveedor "1" --> "N" Compra
    Cliente "1" --> "N" Venta
    Categoria "1" --> "N" Inventario
    Inventario "1" --> "N" UnidadMedida
    Inventario "1" --> "N" LotesProducto
    Inventario "1" --> "N" DetalleCompra
    Inventario "1" --> "N" DetalleVenta
    Compra "1" --> "N" DetalleCompra
    Venta "1" --> "N" DetalleVenta
    UnidadMedida "1" --> "N" DetalleCompra
    UnidadMedida "1" --> "N" DetalleVenta
