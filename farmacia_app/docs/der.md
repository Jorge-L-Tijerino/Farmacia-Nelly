```mermaid
flowchart BT

%% === ENTIDADES ===
Personal[Personal]
Cuenta[Cuenta]
Proveedor[Proveedor]
Cliente[Cliente]
Inventario[Inventario]
Categoria[Categoria]
UnidadMedida[UnidadMedida]
LotesProducto[LotesProducto]
Compra[Compra]
DetalleCompra[DetalleCompra]
Venta[Venta]
DetalleVenta[DetalleVenta]

%% === ATRIBUTOS UNIDOS A ENTIDADES ===
Id_Empleado((Id_Empleado PK)) --- Personal
NombreEmpleado((Nombre)) --- Personal
Cedula((Cedula)) --- Personal
Telefono((Telefono)) --- Personal
DiasTrabajo((DiasTrabajo)) --- Personal
HoraEntrada((HoraEntrada)) --- Personal
HoraSalida((HoraSalida)) --- Personal
Turno((Turno)) --- Personal

Id_Usuario((Id_Usuario PK)) --- Cuenta
Rol((Rol)) --- Cuenta
EstadoCuenta((Estado)) --- Cuenta
Correo((Correo)) --- Cuenta
Pass((Pass)) --- Cuenta

Id_Proveedor((Id_Proveedor PK)) --- Proveedor
TipoProveedor((Tipo)) --- Proveedor
NombreProveedor((Nombre)) --- Proveedor
TelefonoProveedor((Telefono)) --- Proveedor
CorreoProveedor((Correo)) --- Proveedor
DireccionProveedor((Direccion)) --- Proveedor
DiaEntrega((DiaEntrega)) --- Proveedor
HoraEntrega((HoraEntrega)) --- Proveedor
EstadoProveedor((Estado)) --- Proveedor

Id_Cliente((Id_Cliente PK)) --- Cliente
NombreCliente((Nombre)) --- Cliente

Id_Medicamento((Id_Medicamento PK)) --- Inventario
NombreMedicamento((Nombre)) --- Inventario
Descripcion((Descripcion)) --- Inventario
Stock((Stock)) --- Inventario

Id_Categoria((Id_Categoria PK)) --- Categoria
NombreCategoria((Nombre)) --- Categoria

Id_UnidadMedida((Id_UnidadMedida PK)) --- UnidadMedida
NombreUnidad((NombreUnidad)) --- UnidadMedida
Equivalencia((Equivalencia)) --- UnidadMedida
PrecioCompra((PrecioCompra)) --- UnidadMedida
Ganancia((Ganancia)) --- UnidadMedida
PrecioVenta((PrecioVenta)) --- UnidadMedida

Id_Lote((Id_Lote PK)) --- LotesProducto
FechaCaducidad((FechaCaducidad)) --- LotesProducto
Cantidad((Cantidad)) --- LotesProducto

Id_Compra((Id_Compra PK)) --- Compra
FechaCompra((FechaCompra)) --- Compra
TotalCompra((Total)) --- Compra

Id_DetalleCompra((Id_DetalleCompra PK)) --- DetalleCompra
CantidadCompra((Cantidad)) --- DetalleCompra
PrecioCompraDet((Precio)) --- DetalleCompra
FechaCaducidadDet((FechaCaducidad)) --- DetalleCompra

Id_Venta((Id_Venta PK)) --- Venta
FechaVenta((Fecha)) --- Venta
MontoTotal((MontoTotal)) --- Venta

Id_DetalleVenta((Id_DetalleVenta PK)) --- DetalleVenta
CantidadVenta((Cantidad)) --- DetalleVenta
PrecioVentaDet((Precio)) --- DetalleVenta

%% === RELACIONES (ROMBOS) ===
TieneCuenta{"Tiene"}
RegistraCompra{"Registra"}
RealizaVenta{"Realiza"}
SuministraInventario{"Suministra"}
PerteneceCategoria{"Pertenece"}
UsaUnidad{"Usa"}
TieneLote{"Tiene"}
IncluyeDetalleCompra{"Incluye"}
IncluyeDetalleVenta{"Incluye"}

%% === CONEXIONES CON CARDINALIDADES ===
Personal --|1,1|--> TieneCuenta
TieneCuenta --|1,n|--> Cuenta

Personal --|1,1|--> RegistraCompra
RegistraCompra --|1,n|--> Compra

Personal --|1,1|--> RealizaVenta
RealizaVenta --|1,n|--> Venta

Proveedor --|1,1|--> SuministraInventario
SuministraInventario --|1,n|--> Inventario

Proveedor --|1,1|--> RegistraCompra
RegistraCompra --|1,n|--> Compra

Cliente --|1,1|--> RealizaVenta
RealizaVenta --|1,n|--> Venta

Categoria --|1,1|--> PerteneceCategoria
PerteneceCategoria --|1,n|--> Inventario

Inventario --|1,1|--> UsaUnidad
UsaUnidad --|1,n|--> UnidadMedida

Inventario --|1,1|--> TieneLote
TieneLote --|1,n|--> LotesProducto

Compra --|1,1|--> IncluyeDetalleCompra
IncluyeDetalleCompra --|1,n|--> DetalleCompra

Venta --|1,1|--> IncluyeDetalleVenta
IncluyeDetalleVenta --|1,n|--> DetalleVenta
