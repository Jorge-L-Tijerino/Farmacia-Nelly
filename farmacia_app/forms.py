from django import forms
from django.forms import modelformset_factory
from .models import (
    Personal,
    Cuenta,
    Proveedor,
    Categoria,
    Inventario,
    UnidadMedida,
    LotesProducto,
    Cliente,
    Compra,
    DetalleCompra,
    Venta,
    DetalleVenta
)
import re
from datetime import datetime

class PersonalForm(forms.ModelForm):
    class Meta:
        model = Personal
        fields = ['Nombre_Empleado','Cedula_Empleado','Telefono_Empleado','DiasTrabajo','HoraEntrada','HoraSalida','Turno']
        labels = {
            'Nombre_Empleado': 'Nombre Completo',
            'Cedula_Empleado': 'Cédula',
            'Telefono_Empleado': 'Teléfono',
            'DiasTrabajo': 'Días de Trabajo',
            'HoraEntrada': 'Hora de Entrada',
            'HoraSalida': 'Hora de Salida',
            'Turno': 'Turno',
        }
        widgets = {
            'Nombre_Empleado': forms.TextInput(attrs={'class': 'form-control'}),
            'Cedula_Empleado': forms.TextInput(attrs={'class': 'form-control'}),
            'Telefono_Empleado': forms.TextInput(attrs={'class': 'form-control'}),
            'DiasTrabajo': forms.TextInput(attrs={'class': 'form-control'}),
            
            'HoraEntrada': forms.TextInput(attrs={'class': 'form-control', 'type': 'time'}),
            'HoraSalida': forms.TextInput(attrs={'class': 'form-control', 'type': 'time'}),
            'Turno': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Matutino','Matutino'),
                ('Vespertino','Vespertino'),
                ('Nocturno','Nocturno'),
            ]),
        }

    # Validación de cédula
    def clean_Cedula_Empleado(self):
        cedula = self.cleaned_data['Cedula_Empleado']
        if not re.match(r'^[A-Z0-9-]+$', cedula):
            raise forms.ValidationError("La cédula solo puede tener números, guiones y una letra mayúscula.")
        return cedula

    # Validación de teléfono
    def clean_Telefono_Empleado(self):
        telefono = self.cleaned_data['Telefono_Empleado']
        if not re.match(r'^[0-9-]+$', telefono):
            raise forms.ValidationError("El teléfono solo puede tener números y guiones.")
        return telefono

    # Validación de días de trabajo
    def clean_DiasTrabajo(self):
        dias = self.cleaned_data['DiasTrabajo']

        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s-]+$', dias):
            raise forms.ValidationError("Los días de trabajo solo pueden tener letras y guiones.")
        return dias

    # Inicializar hora actual en formato 12 horas (AM/PM)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = datetime.now().strftime("%I:%M %p")  # hh:mm AM/PM
        self.fields['HoraEntrada'].initial = now
        self.fields['HoraSalida'].initial = now


class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ['Id_Empleado','Rol','Estado','Correo_Empleados','Pass']
        labels = {
            'Id_Empleado': 'Empleado',
            'Rol': 'Rol',
            'Estado': 'Estado',
            'Correo_Empleados': 'Correo',
            'Pass': 'Contraseña',
        }
        widgets = {
            #'Id_Empleado': forms.Select(attrs={'class': 'form-control'}),
            'Rol': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Administrador','Administrador'),
                ('Cajero','Cajero'),
            ]),
            'Estado': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Activo','Activo'),
                ('Inactivo','Inactivo'),
            ]),
            'Correo_Empleados': forms.EmailInput(attrs={'class': 'form-control'}),
            'Pass': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    # Validación de correo
    def clean_Correo_Empleados(self):
        correo = self.cleaned_data['Correo_Empleados']
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', correo):
            raise forms.ValidationError("Ingrese un correo válido.")
        return correo
    
class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'Tipo_Proveedor',
            'Nombre_Proveedor',
            'Telefono_Proveedor',
            'Correo_Proveedor',
            'Direccion_Proveedor',
            'DiaEntrega',
            'HoraEntrega',
            'Estado_Proveedor'
        ]
        labels = {
            'Tipo_Proveedor': 'Tipo De Proveedor',
            'Nombre_Proveedor': 'Nombre Completo',
            'Telefono_Proveedor': 'Teléfono',
            'Correo_Proveedor': 'Correo',
            'Direccion_Proveedor': 'Dirección',
            'DiaEntrega': 'Día De Entrega',
            'HoraEntrega': 'Hora De Entrega',
            'Estado_Proveedor': 'Estado',
        }
        widgets = {
            'Tipo_Proveedor': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Empresa', 'Empresa'),
                ('Distribuidor', 'Distribuidor'),
            ]),
            'Nombre_Proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'Telefono_Proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'Correo_Proveedor': forms.EmailInput(attrs={'class': 'form-control'}),
            'Direccion_Proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'DiaEntrega': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Domingo', 'Domingo'),
                ('Lunes', 'Lunes'),
                ('Martes', 'Martes'),
                ('Miércoles', 'Miércoles'),
                ('Jueves', 'Jueves'),
                ('Viernes', 'Viernes'),
                ('Sábado', 'Sábado'),
            ]),
            # Usamos TextInput con type="time" para que sea compatible con AM/PM si lo manejas con JS
            'HoraEntrega': forms.TextInput(attrs={'class': 'form-control', 'type': 'time'}),
            'Estado_Proveedor': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Activo', 'Activo'),
                ('Inactivo', 'Inactivo'),
            ]),
        }

    # Validación de teléfono
    def clean_Telefono_Proveedor(self):
        telefono = self.cleaned_data['Telefono_Proveedor']
        if not re.match(r'^[0-9-]+$', telefono):
            raise forms.ValidationError("El teléfono solo puede tener números y guiones.")
        return telefono

    # Validación de correo
    def clean_Correo_Proveedor(self):
        correo = self.cleaned_data['Correo_Proveedor']
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', correo):
            raise forms.ValidationError("Ingrese un correo válido.")
        return correo

    # Inicializar hora actual en formato 12 horas (AM/PM)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = datetime.now().strftime("%I:%M %p")  # hh:mm AM/PM
        self.fields['HoraEntrega'].initial = now

class CategoriaForm(forms.ModelForm):
    class Meta:
        model= Categoria
        fields = ['Nombre_Categoria']
        labels = {'Nombre_Categoria': 'Categoría',}
        widgets = {'Nombre_Categoria': forms.TextInput(attrs={'class': 'form-control'}), }

class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['Nombre_Medicamento', 'Descripcion', 'Id_Proveedor', 'Id_Categoria', 'Stock']
        labels = {
            'Nombre_Medicamento': 'Producto',
            'Descripcion': 'Descripción',
            'Id_Proveedor': 'Proveedor',
            'Id_Categoria': 'Categoría',
            'Stock': 'Stock',
        }
        widgets = {
            'Nombre_Medicamento': forms.TextInput(attrs={'class': 'form-control'}),
            'Descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            # 👇 Cambiados a HiddenInput porque se manejan con modales de selección
            'Id_Proveedor': forms.HiddenInput(),
            'Id_Categoria': forms.HiddenInput(),
            'Stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    # Validación de stock
    def clean_Stock(self):
        stock = self.cleaned_data['Stock']
        if stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo.")
        return stock

class UnidadMedidaForm(forms.ModelForm):
    class Meta:
        model = UnidadMedida
        fields = ['Id_Medicamento', 'NombreUnidad', 'Equivalencia', 'Precio_Compra', 'Precio_Venta']
        labels = {
            'Id_Medicamento': 'Producto',
            'NombreUnidad': 'Unidad',
            'Equivalencia': 'Equivalencia',
            'Precio_Compra': 'Precio de Compra',
            'Precio_Venta': 'Precio de Venta',
        }
        widgets = {
            # 👇 Se maneja con modal_productos.html
            'Id_Medicamento': forms.HiddenInput(),
            'NombreUnidad': forms.TextInput(attrs={'class': 'form-control'}),
            'Equivalencia': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'Precio_Compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'Precio_Venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
        }

    # Validación de equivalencia
    def clean_Equivalencia(self):
        equivalencia = self.cleaned_data['Equivalencia']
        if equivalencia <= 0:
            raise forms.ValidationError("La equivalencia debe ser mayor que cero.")
        return equivalencia

    # Validación de precios
    def clean(self):
        cleaned_data = super().clean()
        precio_compra = cleaned_data.get('Precio_Compra')
        precio_venta = cleaned_data.get('Precio_Venta')

        if precio_compra is not None and precio_venta is not None:
            if precio_venta < precio_compra:
                raise forms.ValidationError("El precio de venta no puede ser menor al precio de compra.")
        return cleaned_data
    
class LotesProductoForm(forms.ModelForm):
    class Meta:
        model = LotesProducto
        fields = ['Id_Medicamento', 'FechaIngreso', 'FechaCaducidad', 'Cantidad']
        labels = {
            'Id_Medicamento': 'Producto',
            'FechaIngreso': 'Fecha de Ingreso',
            'FechaCaducidad': 'Fecha de Caducidad',
            'Cantidad': 'Cantidad',
        }
        widgets = {
            'Id_Medicamento': forms.HiddenInput(),  # se maneja con modal de selección
            'FechaIngreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'FechaCaducidad': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    # Validación de cantidad
    def clean_Cantidad(self):
        cantidad = self.cleaned_data['Cantidad']
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor que cero.")
        return cantidad

    # Validación de fechas
    def clean(self):
        cleaned_data = super().clean()
        fecha_ingreso = cleaned_data.get('FechaIngreso')
        fecha_caducidad = cleaned_data.get('FechaCaducidad')

        if fecha_ingreso and fecha_caducidad:
            if fecha_caducidad <= fecha_ingreso:
                raise forms.ValidationError("La fecha de caducidad debe ser posterior a la fecha de ingreso.")
        return cleaned_data
    

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['Nombre_Cliente', 'Telefono_Cliente', 'Direccion_Cliente']
        widgets = {
            'Nombre_Cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'Telefono_Cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'Direccion_Cliente': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    # Validación de teléfono
    def clean_Telefono_Cliente(self):
        telefono = self.cleaned_data['Telefono_Cliente']
        if not re.match(r'^[0-9-]+$', telefono):
            raise forms.ValidationError("El teléfono solo puede tener números y guiones.")
        return telefono
    
# Formulario de Login
class LoginForm(forms.Form):
    Correo_Empleados = forms.EmailField(
        label="Usuario",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    Pass = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['Id_Proveedor', 'TotalCompra']
        widgets = {
            'Id_Proveedor': forms.HiddenInput(),
            'TotalCompra': forms.HiddenInput(),
        }


class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['Id_Medicamento', 'Id_UnidadMedida', 'Cantidad', 'PrecioUnitario', 'CostoTotal', 'Fecha']
        widgets = {
            'Id_Medicamento': forms.Select(attrs={'class': 'form-control'}),
            'Id_UnidadMedida': forms.Select(attrs={'class': 'form-control'}),
            'Cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'PrecioUnitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'CostoTotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'Fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

# Formset para manejar múltiples detalles (como el DataGridView viejo)
DetalleCompraFormSet = modelformset_factory(
    DetalleCompra,
    form=DetalleCompraForm,
    extra=1,
    can_delete=True
)

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['Id_Cliente', 'MontoTotal']
        widgets = {
            'Id_Cliente': forms.HiddenInput(),
            'MontoTotal': forms.HiddenInput(),
        }


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = [
            'Id_Medicamento',
            'Id_UnidadMedida',
            'Cantidad',
            'Precio',
            'Monto',
            'Fecha',
            'Id_Lote'
        ]
        widgets = {
            'Id_Medicamento': forms.Select(attrs={'class': 'form-control'}),
            'Id_UnidadMedida': forms.Select(attrs={'class': 'form-control'}),
            'Cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'Precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'Monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'Fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Id_Lote': forms.Select(attrs={'class': 'form-control'}),
        }

# Formset para manejar múltiples detalles (como el DataGridView viejo)
DetalleVentaFormSet = modelformset_factory(
    DetalleVenta,
    form=DetalleVentaForm,
    extra=1,
    can_delete=True
)