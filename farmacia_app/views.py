from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from datetime import date, timedelta
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.db.models import Sum

# Formularios
from .forms import (
    PersonalForm,
    CuentaForm,
    ProveedorForm,
    CategoriaForm,
    InventarioForm,
    UnidadMedidaForm,
    LotesProductoForm,
    ClienteForm,
    LoginForm,
    CompraForm,
    DetalleCompraFormSet,
    VentaForm,
    DetalleVentaFormSet
)

# Modelos
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


# Login 
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['Correo_Empleados']
            password = form.cleaned_data['Pass']

            try:
                cuenta = Cuenta.objects.get(Correo_Empleados=correo, Pass=password)

                # Validar estado
                if cuenta.Estado != "Activo":
                    messages.error(request, "La cuenta está inactiva.")
                    return render(request, "paginas/login.html", {"form": form})

                # Guardar datos en sesión
                request.session['IdEmpleado'] = cuenta.Id_Empleado_id
                request.session['Rol'] = cuenta.Rol

                # Redirigir siempre al index (Skydash)
                return redirect("inicio")

            except Cuenta.DoesNotExist:
                messages.error(request, "Correo o contraseña incorrectos.")
                return render(request, "paginas/login.html", {"form": form})
    else:
        form = LoginForm()

    return render(request, "paginas/login.html", {"form": form})

# Vista Principal
def inicio(request):
    if 'IdEmpleado' not in request.session:
        return redirect('login')

    empleado = None
    try:
        empleado = Personal.objects.get(Id_Empleado=request.session['IdEmpleado'])
    except Personal.DoesNotExist:
        empleado = None

    # Métricas principales
    ventas_hoy = Venta.objects.filter(Fecha=date.today()).aggregate(Sum('MontoTotal'))['MontoTotal__sum'] or 0
    ventas_mes = Venta.objects.filter(Fecha__month=date.today().month).aggregate(Sum('MontoTotal'))['MontoTotal__sum'] or 0
    total_clientes = Cliente.objects.count()
    productos_bajo_stock = Inventario.objects.filter(Stock__lte=15).count()

    # Gráfica: ventas por día (última semana)
    dias_semana = []
    ventas_semana = []
    for i in range(7):
        dia = date.today() - timedelta(days=i)
        dias_semana.insert(0, dia.strftime("%d-%m"))
        total_dia = Venta.objects.filter(Fecha=dia).aggregate(Sum('MontoTotal'))['MontoTotal__sum'] or 0
        ventas_semana.insert(0, total_dia)

    # Gráfica: productos más vendidos
    productos_vendidos = []
    cantidades_vendidas = []
    top_productos = DetalleVenta.objects.values('Id_Medicamento__Nombre_Medicamento') \
        .annotate(total_cantidad=Sum('Cantidad')).order_by('-total_cantidad')[:5]
    for p in top_productos:
        productos_vendidos.append(p['Id_Medicamento__Nombre_Medicamento'])
        cantidades_vendidas.append(p['total_cantidad'])

    # Gráfica: comparativa mensual (ventas vs compras)
    meses = []
    ventas_mensuales = []
    compras_mensuales = []
    for m in range(1, 13):
        meses.append(date(2026, m, 1).strftime("%b"))
        ventas_mensuales.append(Venta.objects.filter(Fecha__month=m).aggregate(Sum('MontoTotal'))['MontoTotal__sum'] or 0)
        compras_mensuales.append(Compra.objects.filter(Fecha__month=m).aggregate(Sum('TotalCompra'))['TotalCompra__sum'] or 0)

    return render(request, 'paginas/index.html', {
        "empleado": empleado,
        "rol": request.session.get("Rol"),
        "ventas_hoy": ventas_hoy,
        "ventas_mes": ventas_mes,
        "total_clientes": total_clientes,
        "productos_bajo_stock": productos_bajo_stock,
        "dias_semana": dias_semana,
        "ventas_semana": ventas_semana,
        "productos_vendidos": productos_vendidos,
        "cantidades_vendidas": cantidades_vendidas,
        "meses": meses,
        "ventas_mensuales": ventas_mensuales,
        "compras_mensuales": compras_mensuales,
    })

# Logout
def logout_view(request):
    request.session.flush()  # limpia toda la sesión
    return redirect("login")

# Inventario
def inventario(request):
    productos = Inventario.objects.all().order_by('pk')
    for producto in productos:
        # 👉 Guardar todas las presentaciones para el modal del ojo
        producto.unidades = UnidadMedida.objects.filter(Id_Medicamento=producto)

        try:
            # 👉 Buscar la presentación "Unidad" para llenar la tabla Inventario
            unidad = UnidadMedida.objects.get(Id_Medicamento=producto, NombreUnidad='Unidad')
            producto.precio_compra = unidad.Precio_Compra
            producto.precio_venta = unidad.Precio_Venta
        except UnidadMedida.DoesNotExist:
            producto.precio_compra = None
            producto.precio_venta = None

    return render(request, 'paginas/inventario.html', {
        'productos': productos,
        'form': InventarioForm(),
        'proveedores': Proveedor.objects.all(),
        'categorias': Categoria.objects.all()
    })

# Agregar Producto
def agregar_inventario(request):
    if request.method == 'POST':
        form = InventarioForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('inventario')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = []
                for field, msgs in form.errors.items():
                    label = form.fields[field].label or field
                    for msg in msgs:
                        errores.append(f"{label}: {msg}")
                return JsonResponse({'success': False, 'errors': errores})
            productos = Inventario.objects.all()
            proveedores = Proveedor.objects.all()
            categorias = Categoria.objects.all()
            return render(request, 'paginas/inventario.html', {
                'form': form,
                'productos': productos,
                'proveedores': proveedores,
                'categorias': categorias
            })
    else:
        form = InventarioForm()
        productos = Inventario.objects.all()
        proveedores = Proveedor.objects.all()
        categorias = Categoria.objects.all()
    return render(request, 'paginas/inventario.html', {
        'form': form,
        'productos': productos,
        'proveedores': proveedores,
        'categorias': categorias
    })

# Editar Producto
def editar_inventario(request, id):
    producto = Inventario.objects.get(pk=id)
    if request.method == 'POST':
        form = InventarioForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('inventario')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = []
                for field, msgs in form.errors.items():
                    label = form.fields[field].label or field
                    for msg in msgs:
                        errores.append(f"{label}: {msg}")
                return JsonResponse({'success': False, 'errors': errores})
    return redirect('inventario')

# Eliminar Producto
def eliminar_inventario(request, id):
    producto = Inventario.objects.get(pk=id)
    if request.method == 'POST':
        producto.delete()
        return redirect('inventario')
    return render(request, 'paginas/inventario.html')

# Unidades De Medida
def unidad_medida(request):
    unidades = UnidadMedida.objects.all().order_by('pk')
    form = UnidadMedidaForm()  # formulario vacío para el modal
    productos = Inventario.objects.all()
    return render(request, 'paginas/unidad_medida.html', {
        'unidades': unidades,
        'form': form,
        'productos': productos
    })

# Agregar Unidad de Medida
def agregar_unidad_medida(request):
    if request.method == 'POST':
        form = UnidadMedidaForm(request.POST)
        if form.is_valid():
            form.save()  # Ganancia se calcula en el modelo
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('unidad_medida')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = [f"{form.fields[field].label or field}: {msg}"
                           for field, msgs in form.errors.items()
                           for msg in msgs]
                return JsonResponse({'success': False, 'errors': errores})
    else:
        form = UnidadMedidaForm()
    unidades = UnidadMedida.objects.all()
    productos = Inventario.objects.all()
    return render(request, 'paginas/unidad_medida.html', {
        'form': form,
        'unidades': unidades,
        'productos': productos
    })

# Editar Unidad de Medida
def editar_unidad_medida(request, id):
    unidad = UnidadMedida.objects.get(pk=id)

    if request.method == 'POST':
        form = UnidadMedidaForm(request.POST, instance=unidad)
        if form.is_valid():
            form.save()  # Ganancia se recalcula en el modelo
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('unidad_medida')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = [f"{form.fields[field].label or field}: {msg}"
                           for field, msgs in form.errors.items()
                           for msg in msgs]
                return JsonResponse({'success': False, 'errors': errores})
    else:
        # 🔑 aquí devuelves el formulario con la instancia
        form = UnidadMedidaForm(instance=unidad)
        return render(request, 'paginas/unidad_medida.html', {
            'form': form,
            'unidades': UnidadMedida.objects.all(),
            'productos': Inventario.objects.all()
        })



# Eliminar Unidad de Medida
def eliminar_unidad_medida(request, id):
    unidad = UnidadMedida.objects.get(pk=id)
    if request.method == 'POST':
        unidad.delete()
        return redirect('unidad_medida')
    return render(request, 'paginas/unidad_medida.html')


# Categorias
def categoria(request):
    categorias = Categoria.objects.all().order_by('pk')
    form = CategoriaForm()
    return render(
        request,
        'paginas/categoria.html',
        {'categorias': categorias, 'form': form}
    )

# Agregar Categoria
def agregar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('categoria')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = []
                for field, msgs in form.errors.items():
                    label = form.fields[field].label or field
                    for msg in msgs:
                        errores.append(f"{label}: {msg}")
                return JsonResponse({'success': False, 'errors': errores})
            categorias = Categoria.objects.all()
            return render(request, 'paginas/categoria.html', {'form': form, 'categorias': categorias})
    else:
        form = CategoriaForm()
        categorias = Categoria.objects.all()
    return render(request, 'paginas/categoria.html', {'form': form, 'categorias': categorias})

# Editar Categoria
def editar_categoria(request, id):
    categoria = Categoria.objects.get(pk=id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('categoria')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = []
                for field, msgs in form.errors.items():
                    label = form.fields[field].label or field
                    for msg in msgs:
                        errores.append(f"{label}: {msg}")
                return JsonResponse({'success': False, 'errors': errores})
    return redirect('categoria')

# Eliminar Categoria
def eliminar_categoria(request, id):
    categoria = Categoria.objects.get(pk=id)
    if request.method == 'POST':
        categoria.delete()
        return redirect('categoria')
    return redirect('categoria')

# Caducidad
def caducidad(request):
    hoy = date.today()
    un_mes_despues = hoy + timedelta(days=30)

    lotes = LotesProducto.objects.all().order_by('pk')
    productos = Inventario.objects.all()
    form = LotesProductoForm()
    return render(request, 'paginas/caducidad.html', {
        'lotes': lotes,
        'form': form,
        'productos': productos,
        'today': hoy,
        'un_mes_despues': un_mes_despues,
    })

# Agregar lote
def agregar_lote(request):
    if request.method == 'POST':
        form = LotesProductoForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('caducidad')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = []
                for field, msgs in form.errors.items():
                    label = form.fields[field].label or field
                    for msg in msgs:
                        errores.append(f"{label}: {msg}")
                return JsonResponse({'success': False, 'errors': errores})
            lotes = LotesProducto.objects.all()
            productos = Inventario.objects.all()
            return render(request, 'paginas/caducidad.html', {
                'form': form,
                'lotes': lotes,
                'productos': productos
            })
    else:
        form = LotesProductoForm()
        lotes = LotesProducto.objects.all()
        productos = Inventario.objects.all()
    return render(request, 'paginas/caducidad.html', {
        'form': form,
        'lotes': lotes,
        'productos': productos
    })

# Editar lote
def editar_lote(request, id):
    lote = LotesProducto.objects.get(pk=id)
    if request.method == 'POST':
        form = LotesProductoForm(request.POST, instance=lote)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('caducidad')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = []
                for field, msgs in form.errors.items():
                    label = form.fields[field].label or field
                    for msg in msgs:
                        errores.append(f"{label}: {msg}")
                return JsonResponse({'success': False, 'errors': errores})
    return redirect('caducidad')

# Eliminar lote
def eliminar_lote(request, id):
    lote = LotesProducto.objects.get(pk=id)
    if request.method == 'POST':
        lote.delete()
        return redirect('caducidad')
    return render(request, 'paginas/caducidad.html')

# Stock Bajo
def stock_bajo(request):
    productos = Inventario.objects.filter(Stock__lte=15).order_by('pk')
    return render(request, 'paginas/stock_bajo.html', {
        'productos': productos
    })
# Proveedores
def proveedores(request):
    proveedores = Proveedor.objects.all().order_by('pk')
    form = ProveedorForm()  # formulario vacío para el modal
    return render(request, 'paginas/proveedores.html', {'proveedores': proveedores, 'form': form})

# Agregar proveedor
def agregar_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('proveedores')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = []
                for field, msgs in form.errors.items():
                    label = form.fields[field].label or field
                    for msg in msgs:
                        errores.append(f"{label}: {msg}")
                return JsonResponse({'success': False, 'errors': errores})
            proveedores = Proveedor.objects.all()
            return render(request, 'paginas/proveedores.html', {'form': form, 'proveedores': proveedores})
    else:
        form = ProveedorForm()
        proveedores = Proveedor.objects.all()
    return render(request, 'paginas/proveedores.html', {'form': form, 'proveedores': proveedores})

# Editar proveedor
def editar_proveedor(request, id):
    proveedor = Proveedor.objects.get(pk=id)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('proveedores')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = []
                for field, msgs in form.errors.items():
                    label = form.fields[field].label or field
                    for msg in msgs:
                        errores.append(f"{label}: {msg}")
                return JsonResponse({'success': False, 'errors': errores})
    return redirect('proveedores')

# Eliminar proveedor
def eliminar_proveedor(request, id):
    proveedor = Proveedor.objects.get(pk=id)
    if request.method == 'POST':
        proveedor.delete()
        return redirect('proveedores')
    return render(request, 'paginas/proveedores.html')


# Empleados
def personal_list(request):
    empleados = Personal.objects.all().order_by('pk')
    form = PersonalForm()  # formulario vacío para el modal
    return render(request, 'paginas/personal.html', {'empleados': empleados, 'form': form})

def cuenta_list(request):
    cuentas = Cuenta.objects.all().order_by('pk')
    empleados = Personal.objects.all()  # lista de empleados
    form = CuentaForm()  # formulario vacío para el modal
    return render(request, 'paginas/cuentas.html', {
        'cuentas': cuentas,
        'form': form,
        'empleados': empleados
    })

# Personal
def agregar_personal(request):
    if request.method == 'POST':
        form = PersonalForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('personal')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = []
                for field, msgs in form.errors.items():
                    label = form.fields[field].label or field
                    for msg in msgs:
                        errores.append(f"{label}: {msg}")
                return JsonResponse({'success': False, 'errors': errores})
            empleados = Personal.objects.all()
            return render(request, 'paginas/personal.html', {'form': form, 'empleados': empleados})
    else:
        form = PersonalForm()
        empleados = Personal.objects.all()
    return render(request, 'paginas/personal.html', {'form': form, 'empleados': empleados})

# Editar personal
def editar_personal(request, id):
    empleado = Personal.objects.get(pk=id)
    if request.method == 'POST':
        form = PersonalForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('personal')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = []
                for field, msgs in form.errors.items():
                    label = form.fields[field].label or field
                    for msg in msgs:
                        errores.append(f"{label}: {msg}")
                return JsonResponse({'success': False, 'errors': errores})
    return redirect('personal')

# Eliminar personal
def eliminar_personal(request, id):
    empleado = Personal.objects.get(pk=id)
    if request.method == 'POST':
        empleado.delete()
        return redirect('personal')
    return render(request, 'paginas/personal.html')

# Cuentas
def agregar_cuenta(request):
    if request.method == 'POST':
        form = CuentaForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('cuentas')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = []
                for field, msgs in form.errors.items():
                    label = form.fields[field].label or field
                    for msg in msgs:
                        errores.append(f"{label}: {msg}")
                return JsonResponse({'success': False, 'errors': errores})
            cuentas = Cuenta.objects.all()
            empleados = Personal.objects.all()
            return render(request, 'paginas/cuentas.html', {
                'form': form,
                'cuentas': cuentas,
                'empleados': empleados
            })
    else:
        form = CuentaForm()
        cuentas = Cuenta.objects.all()
        empleados = Personal.objects.all()
    return render(request, 'paginas/cuentas.html', {
        'form': form,
        'cuentas': cuentas,
        'empleados': empleados
    })

# Editar cuenta
def editar_cuenta(request, id):
    cuenta = Cuenta.objects.get(pk=id)
    if request.method == 'POST':
        form = CuentaForm(request.POST, instance=cuenta)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('cuentas')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = []
                for field, msgs in form.errors.items():
                    label = form.fields[field].label or field
                    for msg in msgs:
                        errores.append(f"{label}: {msg}")
                return JsonResponse({'success': False, 'errors': errores})
    return redirect('cuentas')

# Eliminar cuenta
def eliminar_cuenta(request, id):
    cuenta = Cuenta.objects.get(pk=id)
    if request.method == 'POST':
        cuenta.delete()
        return redirect('cuentas')
    return render(request, 'paginas/cuentas.html')

# Clientes
def clientes(request):
    clientes = Cliente.objects.all().order_by('pk')
    form = ClienteForm()
    return render(
        request,
        'paginas/clientes.html',
        {'clientes': clientes, 'form': form}
    )

# Agregar Cliente
def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('clientes')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # devolvemos los errores como lista
                errores = []
                for field, msgs in form.errors.items():
                    label = form.fields[field].label or field
                    for msg in msgs:
                        errores.append(f"{label}: {msg}")
                return JsonResponse({'success': False, 'errors': errores})
            clientes = Cliente.objects.all()
            return render(request, 'paginas/clientes.html', {'form': form, 'clientes': clientes})
    else:
        form = ClienteForm()
        clientes = Cliente.objects.all()
    return render(request, 'paginas/clientes.html', {'form': form, 'clientes': clientes})

# Editar Cliente
def editar_cliente(request, id):
    cliente = Cliente.objects.get(pk=id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('clientes')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = []
                for field, msgs in form.errors.items():
                    label = form.fields[field].label or field
                    for msg in msgs:
                        errores.append(f"{label}: {msg}")
                return JsonResponse({'success': False, 'errors': errores})
    return redirect('clientes')

# Eliminar Cliente
def eliminar_cliente(request, id):
    cliente = Cliente.objects.get(pk=id)
    if request.method == 'POST':
        cliente.delete()
        return redirect('clientes')
    return render(request, 'paginas/clientes.html')

#Compras
#Registrar Compras
def registro_compra(request):
    if not request.session.get('IdEmpleado'):
        return redirect('login')

    compra_form = CompraForm()
    detalle_formset = DetalleCompraFormSet(queryset=[])
    tabla_local = request.session.get('tabla_local', [])

    proveedores = Proveedor.objects.all()
    productos = Inventario.objects.all()
    unidades = UnidadMedida.objects.all()

    return render(request, 'paginas/registro_compra.html', {
        'compra_form': compra_form,
        'detalle_formset': detalle_formset,
        'tabla_local': tabla_local,
        'proveedores': proveedores,
        'productos': productos,
        'unidades': unidades
    })

# Agregar detalle a la tabla local
def agregar_compra_local(request):
    if request.method == "POST":
        producto_id = request.POST.get("producto_id")
        unidad_id = request.POST.get("unidad_id")
        cantidad = int(request.POST.get("cantidad"))
        fecha_caducidad = request.POST.get("fecha_caducidad")

        producto = Inventario.objects.get(pk=producto_id)
        unidad = UnidadMedida.objects.get(pk=unidad_id)

        detalle = {
    "producto_id": producto.Id_Medicamento,
    "producto_nombre": producto.Nombre_Medicamento,
    "stock_actual": producto.Stock,
    "unidad_id": unidad.Id_UnidadMedida,
    "unidad_nombre": unidad.NombreUnidad,
    "cantidad": cantidad,
    "precio": float(unidad.Precio_Compra),
    "fecha": fecha_caducidad,
    "costo_total": float(cantidad) * float(unidad.Precio_Compra),
}


        tabla_local = request.session.get("tabla_local", [])
        tabla_local.append(detalle)
        request.session["tabla_local"] = tabla_local

        return JsonResponse({"success": True, "tabla_local": tabla_local})


# Editar detalle en tabla local
def editar_compra_local(request, id):
    tabla_local = request.session.get('tabla_local', [])
    if 0 <= id < len(tabla_local):
        if request.method == 'POST':
            tabla_local[id]['cantidad'] = int(request.POST.get('cantidad'))
            tabla_local[id]['unidad_id'] = int(request.POST.get('unidad_id'))
            tabla_local[id]['unidad_nombre'] = request.POST.get('unidad_nombre')

            precio_str = request.POST.get('precio')
            if precio_str:
                precio_str = precio_str.replace(',', '.')  # 🔑 normalizar
                tabla_local[id]['precio'] = float(precio_str)

            tabla_local[id]['fecha'] = request.POST.get('fecha_caducidad')
            tabla_local[id]['costo_total'] = tabla_local[id]['cantidad'] * tabla_local[id]['precio']
            request.session['tabla_local'] = tabla_local
            return JsonResponse({"success": True, "tabla_local": tabla_local})
    return JsonResponse({"success": False})

# Eliminar detalle de tabla local
def eliminar_compra_local(request, id):
    tabla_local = request.session.get('tabla_local', [])
    if 0 <= id < len(tabla_local):
        tabla_local.pop(id)
        request.session['tabla_local'] = tabla_local
        return JsonResponse({"success": True, "tabla_local": tabla_local})
    return JsonResponse({"success": False})

#Cancelar Compra
def cancelar_compra(request):
    request.session['tabla_local'] = []
    return JsonResponse({"success": True})

# Registrar compra en BD
def registrar_compra(request):
    if not request.session.get('IdEmpleado'):
        return redirect('login')

    if request.method == 'POST':
        proveedor_str = request.POST.get("proveedorId")
        fecha_str = request.POST.get("fechaCompra")

        # Validar proveedor
        if not proveedor_str or not proveedor_str.isdigit():
            messages.warning(request, "⚠ Debe seleccionar un proveedor válido.")
            return redirect('registro_compra')

        proveedor = int(proveedor_str)

        # Validar fecha
        if not fecha_str:
            messages.warning(request, "⚠ Debe seleccionar una fecha de compra.")
            return redirect('registro_compra')

        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            messages.warning(request, "⚠ Formato de fecha inválido.")
            return redirect('registro_compra')

        empleado = int(request.session['IdEmpleado'])
        tabla_local = request.session.get('tabla_local', [])

        if not tabla_local:
            messages.warning(request, "⚠ Debe agregar al menos un producto antes de registrar la compra.")
            return redirect('registro_compra')

        total = sum(float(d['costo_total']) for d in tabla_local)

        # Llamada al procedimiento principal
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT insertarcompra(%s,%s,%s,%s)',
                [proveedor, empleado, fecha, total]
            )
            id_compra = cursor.fetchone()[0]

        #Insertar Detalles
        for d in tabla_local:
            fecha_cad = datetime.strptime(d['fecha'], "%Y-%m-%d").date()
            if fecha_cad < datetime.now().date():
                messages.error(request, f"La fecha de caducidad de {d['producto_nombre']} no puede ser menor a hoy.")
                return redirect('registro_compra')

            # ✅ Llamada en minúsculas
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT insertardetallecompra(%s,%s,%s,%s,%s,%s,%s)
                """, [
                    id_compra,
                    fecha_cad,
                    int(d['producto_id']),
                    int(d['unidad_id']),
                    int(d['cantidad']),
                    float(d['precio']),
                    float(d['costo_total'])
                ])

            unidad = UnidadMedida.objects.get(pk=d['unidad_id'])
            equivalencia = unidad.Equivalencia
            cantidad_real = int(d['cantidad']) * equivalencia

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO "LotesProducto" ("Id_Medicamento", "FechaIngreso", "FechaCaducidad", "Cantidad")
                    VALUES (%s, %s, %s, %s)
                """, [
                    int(d['producto_id']),
                    datetime.now().date(),
                    fecha_cad,
                    cantidad_real
                ])

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE "ProductosFarmaceuticos"
                    SET "Stock" = "Stock" + %s
                    WHERE "Id_Medicamento" = %s
                """, [
                    cantidad_real,
                    int(d['producto_id'])
                ])

        request.session['tabla_local'] = []
        messages.success(request, "Compra registrada exitosamente en la BD.")
        return redirect('consulta_compras')

    return redirect('registro_compra')


#Devuelve las Unidades
def unidades_por_producto(request, producto_id):
    unidades = UnidadMedida.objects.filter(Id_Medicamento=producto_id)
    data = [
        {
            "id": u.Id_UnidadMedida,
            "nombre": u.NombreUnidad,
            "equivalencia": u.Equivalencia,
            "precio": float(u.Precio_Compra)
        }
        for u in unidades
    ]
    return JsonResponse({"unidades": data})


# Consulta de compras (historial en BD)
def consulta_compras(request):
    if not request.session.get('IdEmpleado'):
        return redirect('login')

    compras = Compra.objects.select_related('Id_Proveedor','Id_Empleado').order_by('-Fecha')
    proveedores = Proveedor.objects.all()
    empleados = Personal.objects.all()

    return render(request, 'paginas/consulta_compras.html', {
        'compras': compras,
        'proveedores': proveedores,
        'empleados': empleados
    })

#Reporte De Compra
def reporte_compra_pdf(request, id_compra):
    compra = Compra.objects.select_related('Id_Proveedor','Id_Empleado').get(pk=id_compra)
    detalles = compra.detallecompra_set.all()

    # Crear respuesta HTTP con PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="reporte_compra_{id_compra}.pdf"'

    # Crear PDF con ReportLab
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Encabezado
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width/2, height-50, "Detalle de Compra")

    p.setFont("Helvetica", 10)
    p.drawString(50, height-80, f"Fecha de Emisión: {compra.Fecha}")
    p.drawString(50, height-95, f"ID Compra: {compra.Id_Compra}")
    p.drawString(50, height-110, f"Proveedor: {compra.Id_Proveedor.Nombre_Proveedor}")
    p.drawString(50, height-125, f"Empleado: {compra.Id_Empleado.Nombre_Empleado}")

    # Tabla de detalles
    y = height-160
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Medicamento")
    p.drawString(200, y, "Unidad")
    p.drawString(300, y, "Cantidad")
    p.drawString(370, y, "Precio Unitario")
    p.drawString(470, y, "Costo Total")

    p.setFont("Helvetica", 10)
    y -= 20
    for detalle in detalles:
        p.drawString(50, y, detalle.Id_Medicamento.Nombre_Medicamento)
        p.drawString(200, y, detalle.Id_UnidadMedida.NombreUnidad)
        p.drawString(300, y, str(detalle.Cantidad))
        p.drawString(370, y, f"{detalle.PrecioUnitario:.2f}")
        p.drawString(470, y, f"{detalle.CostoTotal:.2f}")
        y -= 20

    # Total y firma
    y -= 20
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, f"Total de Compra: {compra.TotalCompra:.2f}")
    y -= 40
    p.drawString(50, y, "Firma del Empleado: __________________________")

    # Finalizar PDF
    p.showPage()
    p.save()

    return response

#Venta
def caja(request):
    if not request.session.get('IdEmpleado'):
        return redirect('login')

    venta_form = VentaForm()
    detalle_formset = DetalleVentaFormSet(queryset=[])
    tabla_local = request.session.get('tabla_local_venta', [])

    clientes = Cliente.objects.all()
    productos = Inventario.objects.all()
    unidades = UnidadMedida.objects.all()
    lotes = LotesProducto.objects.all()

    today=date.today()

    return render(request, 'paginas/caja.html', {
        'venta_form': venta_form,
        'detalle_formset': detalle_formset,
        'tabla_local': tabla_local,
        'clientes': clientes,
        'productos': productos,
        'unidades': unidades,
        'lotes': lotes,
        'today': today
    })

# Agregar detalle a la tabla local de ventas
def agregar_venta_local(request):
    if request.method == "POST":
        producto_id = request.POST.get("producto_id")
        unidad_id = request.POST.get("unidad_id")
        cantidad = int(request.POST.get("cantidad"))
        lote_id = request.POST.get("lote_id")

        producto = Inventario.objects.get(pk=producto_id)
        unidad = UnidadMedida.objects.get(pk=unidad_id)
        lote = LotesProducto.objects.get(pk=lote_id)

        equivalencia = unidad.Equivalencia
        cantidad_real = cantidad * equivalencia
        if cantidad_real > producto.Stock:
            return JsonResponse({"success": False, "error": "Stock insuficiente"})
        if cantidad_real > lote.Cantidad:
            return JsonResponse({"success": False, "error": "Cantidad excede el lote disponible"})

        detalle = {
            "producto_id": producto.Id_Medicamento,
            "producto_nombre": producto.Nombre_Medicamento,
            "unidad_id": unidad.Id_UnidadMedida,
            "unidad_nombre": unidad.NombreUnidad,
            "cantidad": cantidad,
            "precio": float(unidad.Precio_Venta),
            "monto": float(cantidad) * float(unidad.Precio_Venta),
            "lote_id": lote.Id_Lote,
            "fecha_caducidad": str(lote.FechaCaducidad),
            "cantidad_disponible": lote.Cantidad,
            "stock_actual": producto.Stock   # 🔑 agregado
        }

        tabla_local = request.session.get("tabla_local_venta", [])
        tabla_local.append(detalle)
        request.session["tabla_local_venta"] = tabla_local

        return JsonResponse({"success": True, "tabla_local": tabla_local})

# Editar detalle en tabla local de ventas
def editar_venta_local(request, id):
    tabla_local = request.session.get('tabla_local_venta', [])
    if 0 <= id < len(tabla_local):
        if request.method == 'POST':
            cantidad = int(request.POST.get('cantidad'))
            unidad_id = int(request.POST.get('unidad_id'))
            unidad_nombre = request.POST.get('unidad_nombre')
            precio_str = request.POST.get('precio')
            lote_id = int(request.POST.get('lote_id'))

            producto = Inventario.objects.get(pk=tabla_local[id]['producto_id'])
            unidad = UnidadMedida.objects.get(pk=unidad_id)
            lote = LotesProducto.objects.get(pk=lote_id)

            equivalencia = unidad.Equivalencia
            cantidad_real = cantidad * equivalencia

            # Validaciones
            if cantidad_real > producto.Stock:
                return JsonResponse({"success": False, "error": "Stock insuficiente"})
            if cantidad_real > lote.Cantidad:
                return JsonResponse({"success": False, "error": "Cantidad excede el lote disponible"})

            # Actualizar detalle
            tabla_local[id]['cantidad'] = cantidad
            tabla_local[id]['unidad_id'] = unidad_id
            tabla_local[id]['unidad_nombre'] = unidad_nombre
            tabla_local[id]['lote_id'] = lote_id
            tabla_local[id]['fecha_caducidad'] = str(lote.FechaCaducidad)
            tabla_local[id]['cantidad_disponible'] = lote.Cantidad   # 🔑 agregado
            tabla_local[id]['stock_actual'] = producto.Stock         # 🔑 agregado

            if precio_str:
                precio_str = precio_str.replace(',', '.')
                tabla_local[id]['precio'] = float(precio_str)

            tabla_local[id]['monto'] = tabla_local[id]['cantidad'] * tabla_local[id]['precio']
            request.session['tabla_local_venta'] = tabla_local
            return JsonResponse({"success": True, "tabla_local": tabla_local})
    return JsonResponse({"success": False})



# Eliminar detalle de tabla local de ventas
def eliminar_venta_local(request, id):
    tabla_local = request.session.get('tabla_local_venta', [])
    if 0 <= id < len(tabla_local):
        tabla_local.pop(id)
        request.session['tabla_local_venta'] = tabla_local
        return JsonResponse({"success": True, "tabla_local": tabla_local})
    return JsonResponse({"success": False})

# Cancelar Venta
def cancelar_venta(request):
    request.session['tabla_local_venta'] = []
    return JsonResponse({"success": True})

# Registrar venta en BD
def registrar_venta(request):
    if not request.session.get('IdEmpleado'):
        return redirect('login')

    if request.method == 'POST':
        cliente_str = request.POST.get("clienteId")
        fecha_str = request.POST.get("fechaVenta")

        # Validar cliente
        if not cliente_str or not cliente_str.isdigit():
            messages.warning(request, "⚠ Debe seleccionar un cliente válido.")
            return redirect('caja')

        cliente = int(cliente_str)

        # Validar fecha
        if not fecha_str:
            messages.warning(request, "⚠ Debe seleccionar una fecha de venta.")
            return redirect('caja')

        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            messages.warning(request, "⚠ Formato de fecha inválido.")
            return redirect('caja')

        empleado = int(request.session['IdEmpleado'])
        tabla_local = request.session.get('tabla_local_venta', [])

        if not tabla_local:
            messages.warning(request, "⚠ Debe agregar al menos un producto antes de registrar la venta.")
            return redirect('caja')

        total = sum(float(d['monto']) for d in tabla_local)

        # Procedimiento principal
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT insertarventa(%s,%s,%s,%s)',
                [cliente, empleado, fecha, total]
            )
            id_venta = cursor.fetchone()[0]

        # Insertar detalles
        for d in tabla_local:
            lote = LotesProducto.objects.get(pk=d['lote_id'])
            equivalencia = UnidadMedida.objects.get(pk=d['unidad_id']).Equivalencia
            cantidad_real = int(d['cantidad']) * equivalencia

            # Validar caducidad
            if lote.FechaCaducidad < datetime.now().date():
                messages.error(request, f"El lote seleccionado para {d['producto_nombre']} ya está vencido.")
                return redirect('caja')

            # Validar stock
            if cantidad_real > lote.Cantidad:
                messages.error(request, f"La cantidad excede el lote disponible de {d['producto_nombre']}.")
                return redirect('caja')

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT insertardetalleventa(%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [
                    id_venta,
                    fecha,
                    cliente,
                    int(d['producto_id']),
                    int(d['unidad_id']),
                    int(d['cantidad']),
                    float(d['precio']),
                    float(d['monto']),
                    int(d['lote_id'])
                ])

            # Actualizar stock y lote
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE "LotesProducto"
                    SET "Cantidad" = "Cantidad" - %s
                    WHERE "Id_Lote" = %s
                """, [cantidad_real, int(d['lote_id'])])

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE "ProductosFarmaceuticos"
                    SET "Stock" = "Stock" - %s
                    WHERE "Id_Medicamento" = %s
                """, [cantidad_real, int(d['producto_id'])])

        request.session['tabla_local_venta'] = []
        messages.success(request, "✔ Venta registrada exitosamente en la BD.")
        return redirect('historial_ventas')

    return redirect('caja')



# Devuelve las Unidades (según producto) con Precio_Venta
def unidades_por_producto_venta(request, producto_id):
    unidades = UnidadMedida.objects.filter(Id_Medicamento=producto_id)
    data = [
        {
            "id": u.Id_UnidadMedida,
            "nombre": u.NombreUnidad,
            "equivalencia": u.Equivalencia,
            "precio": float(u.Precio_Venta)
        }
        for u in unidades
    ]
    return JsonResponse({"unidades": data})

# Devuelve los lotes según producto
def lotes_por_producto(request, producto_id):
    lotes = LotesProducto.objects.filter(Id_Medicamento=producto_id)
    data = [
        {
            "id": l.Id_Lote,
            "fecha_caducidad": str(l.FechaCaducidad),
            "cantidad": l.Cantidad
        }
        for l in lotes
    ]
    return JsonResponse({"lotes": data})


# Historial de ventas
def historial_ventas(request):
    if not request.session.get('IdEmpleado'):
        return redirect('login')

    ventas = Venta.objects.select_related('Id_Cliente','Id_Empleado').order_by('-Fecha')
    clientes = Cliente.objects.all()
    empleados = Personal.objects.all()

    return render(request, 'paginas/historial_ventas.html', {
        'ventas': ventas,
        'clientes': clientes,
        'empleados': empleados
    })

# Reporte de Venta en PDF
def reporte_venta_pdf(request, id_venta):
    venta = Venta.objects.select_related('Id_Cliente','Id_Empleado').get(pk=id_venta)
    detalles = venta.detalleventa_set.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="reporte_venta_{id_venta}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Encabezado
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width/2, height-50, "Detalle de Venta")

    p.setFont("Helvetica", 10)
    p.drawString(50, height-80, f"Fecha de Emisión: {venta.Fecha}")
    p.drawString(50, height-95, f"ID Venta: {venta.Id_Venta}")
    p.drawString(50, height-110, f"Cliente: {venta.Id_Cliente.Nombre_Cliente}")
    p.drawString(50, height-125, f"Empleado: {venta.Id_Empleado.Nombre_Empleado}")

    # Tabla de detalles
    y = height-160
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Medicamento")
    p.drawString(200, y, "Unidad")
    p.drawString(300, y, "Cantidad")
    p.drawString(370, y, "Precio")
    p.drawString(470, y, "Monto")

    p.setFont("Helvetica", 10)
    y -= 20
    for detalle in detalles:
        p.drawString(50, y, detalle.Id_Medicamento.Nombre_Medicamento)
        p.drawString(200, y, detalle.Id_UnidadMedida.NombreUnidad)
        p.drawString(300, y, str(detalle.Cantidad))
        p.drawString(370, y, f"{detalle.Precio:.2f}")
        p.drawString(470, y, f"{detalle.Monto:.2f}")
        y -= 20

    # Total y firma
    y -= 20
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, f"Total de Venta: {venta.MontoTotal:.2f}")
    y -= 40
    p.drawString(50, y, "Firma del Empleado: __________________________")

    # Finalizar PDF
    p.showPage()
    p.save()

    return response



# Create your views here.
