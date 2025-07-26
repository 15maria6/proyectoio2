from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.urls import reverse
from urllib.parse import quote
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Cliente 



def registro_view(request):
    if request.method == 'POST':
        nombre_completo = request.POST.get('nombre_completo')  # <-- capturamos el nombre
        password = request.POST.get('password')
        email = request.POST.get('email')
        celular = request.POST.get('celular')
        direccion = request.POST.get('direccion')

        # Usamos el nombre_completo como username
        if User.objects.filter(username=nombre_completo).exists():
            messages.error(request, "Este usuario ya existe.")
            return redirect('registro')

        # Creamos el usuario usando nombre_completo como username
        user = User.objects.create_user(
            username=nombre_completo,
            password=password,
            email=email,
            first_name=nombre_completo  # opcional, para mostrar en plantilla
        )

        # Creamos el Cliente
        Cliente.objects.create(usuario=user, celular=celular, direccion=direccion)

        login(request, user)  # Inicia sesión automáticamente
        return redirect('ver_carrito')

    return render(request, 'tienda/registro.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect('ver_carrito')  # o donde quieras
        else:
            messages.error(request, 'Correo o contraseña incorrectos')

    return render(request, 'tienda/login.html')


def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    carrito = request.session.get('carrito', {})

    cantidad = int(request.POST.get('cantidad', 1))
    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += cantidad
        
    else:
        carrito[str(producto_id)] = {
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'cantidad': cantidad,
            
        }

    request.session['carrito'] = carrito
    request.session['agregados_count'] = len(carrito)
    return redirect('ver_carrito')
def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    total = 0
    items = []

    for key, item in carrito.items():
        precio = float(item['precio'])
        cantidad = item['cantidad']
        subtotal = precio * cantidad
        total += subtotal
        items.append({
            'id': key,  # Este 'id' se usa en los botones + y -
            'nombre': item['nombre'],
            'precio': f"{precio:.2f}",
            'cantidad': cantidad,
            'subtotal': f"{subtotal:.2f}",
        })

    return render(request, 'tienda/carrito.html', {
        'items': items,
        'total': f"{total:.2f}",
        'agregados_count': len(carrito),
    })



def lista_productos(request):
    productos = Producto.objects.all()
    carrito = request.session.get('carrito', {})
    request.session['agregados_count'] = len(carrito)  # ✅

    return render(request, 'tienda/productos.html', {
        'productos': productos,
        'agregados_count': len(carrito),
    })

#mensaje de whastapp
from urllib.parse import quote

@login_required(login_url='login')
def finalizar_pedido(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        return redirect('ver_carrito')

    # Obtener datos del cliente desde POST
    user = request.user
    nombre = user.get_full_name() or user.username
    correo = user.email
    celular = user.profile.celular if hasattr(user, 'profile') else 'No especificado'
    direccion = user.profile.direccion if hasattr(user, 'profile') else 'No especificada'

    
    mensaje = "🛍️ *Nuevo Pedido*\n"
    total = 0

    for item in carrito.values():
        subtotal = float(item['precio']) * item['cantidad']
        total += subtotal
        mensaje += f"- {item['nombre']} x{item['cantidad']} = Bs {subtotal:.2f}\n"

    mensaje += f"\n💰 *Total a pagar:* Bs {total:.2f}"
    mensaje += f"\n\n👤 *Nombre:* {nombre or 'No especificado'}"
    mensaje += f"\n📞 *Celular:* {celular or 'No especificado'}"
    mensaje += f"\n📧 *Correo:* {correo or 'No especificado'}"
    mensaje += f"\n📍 *Dirección:* {direccion or 'No especificada'}"

    # Número del vendedor (cambia 5917xxxxxxx por uno real)
    numero_vendedor = "59179730325"
    enlace = f"https://wa.me/{numero_vendedor}?text={quote(mensaje)}"

    # Limpia el carrito después de enviar
    request.session['carrito'] = {}
    request.session['agregados_count'] = 0

    return redirect(enlace)

#bacia el carrito despues pedido

@require_POST
def actualizar_cantidad(request):
    producto_id = str(request.POST.get('producto_id'))  # Convertido a str

    try:
        nueva_cantidad = int(request.POST.get('cantidad'))
    except (ValueError, TypeError):
        return redirect('ver_carrito')

    carrito = request.session.get('carrito', {})

    if producto_id in carrito:
        if nueva_cantidad > 0:
            carrito[producto_id]['cantidad'] = nueva_cantidad
        else:
            del carrito[producto_id]  # Si es 0, se elimina
        request.session['carrito'] = carrito

    return redirect('ver_carrito')

@require_POST
def eliminar_producto(request):
    nombre = request.POST.get('nombre')
    carrito = request.session.get('carrito', {})
    
    # Elimina producto por nombre
    producto_id_a_eliminar = None
    for producto_id, item in carrito.items():
        if item['nombre'] == nombre:
            producto_id_a_eliminar = producto_id
            break

    if producto_id_a_eliminar:
        del carrito[producto_id_a_eliminar]
        request.session['carrito'] = carrito
        request.session['agregados_count'] = len(carrito)

    return redirect('ver_carrito')
# cuenta
def cuenta(request):
    return render(request, 'tienda/cuenta.html')
def panel_vendedor(request):
    return render(request, 'tienda/vendedor.html')

