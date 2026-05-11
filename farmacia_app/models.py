# Create your models here.
from django.db import models

class Personal(models.Model):
    Id_Empleado = models.AutoField(primary_key=True, db_column='Id_Empleado')
    Nombre_Empleado = models.CharField(max_length=100, db_column='Nombre_Empleado')
    Cedula_Empleado = models.CharField(max_length=100, db_column='Cedula_Empleado')
    Telefono_Empleado = models.CharField(max_length=100, db_column='Telefono_Empleado')
    DiasTrabajo = models.CharField(max_length=50, db_column='DiasTrabajo')
    HoraEntrada = models.TimeField(db_column='HoraEntrada')
    HoraSalida = models.TimeField(db_column='HoraSalida')
    Turno = models.CharField(max_length=50, db_column='Turno')

    class Meta:
        db_table = '"Personal"'   # con comillas y mayúscula

    def __str__(self):
        return self.Nombre_Empleado


class Cuenta(models.Model):
    Id_Usuario = models.AutoField(primary_key=True, db_column='Id_Usuario')
    Id_Empleado = models.ForeignKey(
        Personal,
        on_delete=models.CASCADE,
        db_column='Id_Empleado',
        default=1
    )
    Rol = models.CharField(max_length=50, db_column='Rol')
    Estado = models.CharField(max_length=50, db_column='Estado')
    Correo_Empleados = models.EmailField(unique=True, db_column='Correo_Empleados')
    Pass = models.CharField(max_length=100, db_column='Pass')

    class Meta:
        db_table = '"Cuenta"'

    def __str__(self):
        return f"{self.Correo_Empleados} - {self.Rol}"


class Proveedor(models.Model):
    Id_Proveedor = models.AutoField(primary_key=True, db_column='Id_Proveedor')
    Tipo_Proveedor = models.CharField(max_length=100, db_column='Tipo_Proveedor')
    Nombre_Proveedor = models.CharField(max_length=100, db_column='Nombre_Proveedor')
    Telefono_Proveedor = models.CharField(max_length=100, db_column='Telefono_Proveedor')
    Correo_Proveedor = models.EmailField(db_column='Correo_Proveedor')
    Direccion_Proveedor = models.CharField(max_length=200, db_column='Direccion_Proveedor')
    DiaEntrega = models.CharField(max_length=50, db_column='DiaEntrega')
    HoraEntrega = models.TimeField(db_column='HoraEntrega')
    Estado_Proveedor = models.CharField(max_length=100, db_column='Estado_Proveedor')

    class Meta:
        db_table = '"Proveedor"'

    def __str__(self):
        return self.Nombre_Proveedor


class Categoria(models.Model):
    Id_Categoria = models.AutoField(primary_key=True, db_column='Id_Categoria')
    Nombre_Categoria = models.CharField(max_length=100, db_column='Nombre_Categoria')

    class Meta:
        db_table = '"Categorias"'

    def __str__(self):
        return self.Nombre_Categoria


class Inventario(models.Model):
    Id_Medicamento = models.AutoField(primary_key=True, db_column='Id_Medicamento')
    Nombre_Medicamento = models.CharField(max_length=100, db_column='Nombre_Medicamento')
    Descripcion = models.CharField(max_length=100, db_column='Descripcion')
    Id_Proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        db_column='Id_Proveedor',
        default=1
    )
    Id_Categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        db_column='Id_Categoria',
        default=1
    )
    Stock = models.IntegerField(db_column='Stock')

    class Meta:
        db_table = '"ProductosFarmaceuticos"'

    def __str__(self):
        return self.Nombre_Medicamento


class UnidadMedida(models.Model):
    Id_UnidadMedida = models.AutoField(primary_key=True, db_column='Id_UnidadMedida')
    Id_Medicamento = models.ForeignKey(
        Inventario,
        on_delete=models.CASCADE,
        db_column='Id_Medicamento',
        default=1
    )
    NombreUnidad = models.CharField(max_length=100, db_column='NombreUnidad')
    Equivalencia = models.IntegerField(db_column='Equivalencia')
    Precio_Compra = models.DecimalField(max_digits=10, decimal_places=2, db_column='Precio_Compra')
    Precio_Venta = models.DecimalField(max_digits=10, decimal_places=2, db_column='Precio_Venta')
    Ganancia = models.IntegerField(db_column='Ganancia')

    class Meta:
        db_table = '"UnidadesMedidaProducto"'

    def save(self, *args, **kwargs):
        if self.Precio_Compra and self.Precio_Venta:
            # 🔑 cálculo en porcentaje entero
            self.Ganancia = round(((self.Precio_Venta - self.Precio_Compra) / self.Precio_Compra) * 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.NombreUnidad} - {self.Id_Medicamento.Nombre_Medicamento}"



class LotesProducto(models.Model):
    Id_Lote = models.AutoField(primary_key=True, db_column='Id_Lote')
    Id_Medicamento = models.ForeignKey(
        Inventario,
        on_delete=models.CASCADE,
        db_column='Id_Medicamento',
        default=1
    )
    FechaIngreso = models.DateField(db_column='FechaIngreso')
    FechaCaducidad = models.DateField(db_column='FechaCaducidad')
    Cantidad = models.IntegerField(db_column='Cantidad')

    class Meta:
        db_table = '"LotesProducto"'

    def __str__(self):
        return f"Lote {self.Id_Lote} - {self.Id_Medicamento.Nombre_Medicamento}"


class Cliente(models.Model):
    Id_Cliente = models.AutoField(primary_key=True, db_column='Id_Cliente')
    Nombre_Cliente = models.CharField(max_length=100, db_column='Nombre_Cliente')
    Telefono_Cliente = models.CharField(max_length=50, db_column='Telefono_Cliente')
    Direccion_Cliente = models.CharField(max_length=200, db_column='Direccion_Cliente')

    class Meta:
        db_table = '"Clientes"'

    def __str__(self):
        return self.Nombre_Cliente

class Compra(models.Model):
    Id_Compra = models.AutoField(primary_key=True, db_column='Id_Compra')
    Id_Proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, db_column='Id_Proveedor')
    Id_Empleado = models.ForeignKey(Personal, on_delete=models.CASCADE, db_column='Id_Empleado')
    Fecha = models.DateField(db_column='Fecha')
    TotalCompra = models.DecimalField(max_digits=10, decimal_places=2, db_column='TotalCompra')

    class Meta:
        db_table = '"Compra"'   # ✅ coincide con la tabla existente en PostgreSQL

    def __str__(self):
        return f"Compra {self.Id_Compra} - Total: {self.TotalCompra}"


class DetalleCompra(models.Model):
    Id_DetalleCompra = models.AutoField(primary_key=True, db_column='Id_DetalleCompra')
    Id_Compra = models.ForeignKey(Compra, on_delete=models.CASCADE, db_column='Id_Compra')
    Fecha = models.DateField(db_column='Fecha')
    Id_Medicamento = models.ForeignKey(Inventario, on_delete=models.CASCADE, db_column='Id_Medicamento')  # ✅ Inventario
    Id_UnidadMedida = models.ForeignKey(UnidadMedida, on_delete=models.CASCADE, db_column='Id_UnidadMedida')  # ✅ UnidadMedida
    Cantidad = models.IntegerField(db_column='Cantidad')
    PrecioUnitario = models.DecimalField(max_digits=10, decimal_places=2, db_column='PrecioUnitario')
    CostoTotal = models.DecimalField(max_digits=10, decimal_places=2, db_column='CostoTotal')

    class Meta:
        db_table = '"DetalleCompra"'

    def __str__(self):
        return f"Detalle {self.Id_DetalleCompra} - Compra {self.Id_Compra_id}"


class Venta(models.Model):
    Id_Venta = models.AutoField(primary_key=True, db_column='Id_Venta')
    Id_Empleado = models.ForeignKey(Personal, on_delete=models.CASCADE, db_column='Id_Empleado')
    Fecha = models.DateField(db_column='Fecha')
    Id_Cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='Id_Cliente')
    MontoTotal = models.DecimalField(max_digits=10, decimal_places=2, db_column='MontoTotal')

    class Meta:
        db_table = '"Venta"'

    def __str__(self):
        return f"Venta {self.Id_Venta} - Total: {self.MontoTotal}"


class DetalleVenta(models.Model):
    Id_DetalleVenta = models.AutoField(primary_key=True, db_column='Id_DetalleVenta')
    Id_Venta = models.ForeignKey(Venta, on_delete=models.CASCADE, db_column='Id_Venta')
    Fecha = models.DateField(db_column='Fecha')
    Id_Cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='Id_Cliente')
    Id_Medicamento = models.ForeignKey(Inventario, on_delete=models.CASCADE, db_column='Id_Medicamento')
    Id_UnidadMedida = models.ForeignKey(UnidadMedida, on_delete=models.CASCADE, db_column='Id_UnidadMedida')
    Cantidad = models.IntegerField(db_column='Cantidad')
    Precio = models.DecimalField(max_digits=10, decimal_places=2, db_column='Precio')
    Monto = models.DecimalField(max_digits=10, decimal_places=2, db_column='Monto')
    Id_Lote = models.ForeignKey(LotesProducto, on_delete=models.CASCADE, db_column='Id_Lote', null=True, blank=True)

    class Meta:
        db_table = '"DetalleVenta"'

    def __str__(self):
        return f"Detalle {self.Id_DetalleVenta} - Venta {self.Id_Venta_id}"

