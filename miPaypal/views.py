# views.py
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .models import Product, TransaccionPaypal, Cart, CartItem, Order, OrderItem
from datetime import datetime
from .customButton import CustomPaypalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decimal import Decimal
import random
import string
from django.views.decorators.http import require_http_methods


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = sum(item.quantity for item in cart.cartitem_set.all())
        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
            'message': f'{product.name} agregado al carrito'
        })
    
    # Redirigir de vuelta a la página desde donde se añadió el producto
    next_url = request.GET.get('next', 'view_cart')
    return redirect(next_url)

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('view_cart')

def update_cart_item(request, item_id):
    if request.method == 'POST':
        quantity = request.POST.get('quantity', 1)
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart_item.quantity = quantity
        cart_item.save()
    return redirect('view_cart')

def view_cart(request):
    cart = get_or_create_cart(request)
    cart_items = cart.cartitem_set.all()
    total = sum(item.total_price() for item in cart_items)
    total_items = sum(item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'total_items': total_items,
    }
    return render(request, 'paypal/cart.html', context)

@login_required(login_url='login-page')
def checkout(request):
    cart = get_or_create_cart(request)
    cart_items = cart.cartitem_set.all()
    
    if not cart_items:
        return redirect('view_cart')
    
    total = sum(item.total_price() for item in cart_items)
    total_items = sum(item.quantity for item in cart_items)
    item_names = ", ".join([item.product.name for item in cart_items])
    
    # Obtener información de entrega desde la sesión o crear nueva
    delivery_info = request.session.get('delivery_info', {
        'delivery_method': 'pickup',
        'delivery_cost': 0
    })
    
    # Calcular total con costo de envío
    delivery_cost = delivery_info.get('delivery_cost', 0)
    total_with_delivery = total + delivery_cost
    
    host = request.get_host()
    paypal_checkout = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': total_with_delivery,
        'item_name': f"Compra de {item_names}",
        'invoice': uuid.uuid4(),
        'currency_code': 'USD',
        'notify_url': f'https://https://3f8c-200-86-235-234.ngrok-free.app/{reverse("paypal-ipn")}',
        'return_url': f'http://{host}{reverse("payment-success")}',
        'cancel_url': f'http://{host}{reverse("payment-failed")}',
        'custom': item_names,
    }
    
    paypal_payment = CustomPaypalPaymentsForm(initial=paypal_checkout)
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'total_items': total_items,
        'delivery_cost': delivery_cost,
        'total_with_delivery': total_with_delivery,
        'delivery_info': delivery_info,
        'paypal': paypal_payment
    }
    return render(request, 'paypal/checkout.html', context)

def payment_successful(request):
    cart = get_or_create_cart(request)
    cart_items = cart.cartitem_set.all()
    
    if cart_items and request.user.is_authenticated:
        # Obtener información de entrega de la sesión
        delivery_info = request.session.get('delivery_info', {
            'delivery_method': 'pickup',
            'delivery_cost': 0
        })
        
        # Crear información de envío básica (se puede expandir con un formulario)
        shipping_info = {
            'address': getattr(request.user, 'direccion', 'Dirección no especificada'),
            'city': 'Ciudad no especificada',
            'phone': getattr(request.user, 'telefono', 'Teléfono no especificado'),
        }
        
        # Crear la orden con información de entrega
        order = create_order_from_cart(request.user, cart, shipping_info, delivery_info)
        
        if order:
            # Actualizar estado de pago como completado
            order.payment_status = 'completed'
            order.save()
            
            # Limpiar información de entrega de la sesión
            if 'delivery_info' in request.session:
                del request.session['delivery_info']
            
            context = {
                'order': order,
                'success_message': f'¡Compra realizada exitosamente! Número de orden: {order.order_number}'
            }
        else:
            context = {'error_message': 'Error al procesar la orden'}
    else:
        # Limpiar el carrito para usuarios no autenticados
        cart_items.delete()
        cart.delete()
        
        # Limpiar información de entrega de la sesión
        if 'delivery_info' in request.session:
            del request.session['delivery_info']
            
        context = {'success_message': '¡Compra realizada exitosamente!'}
    
    return render(request, 'paypal/payment-success.html', context)

def payment_failed(request):
    return render(request, 'paypal/payment-failed.html')

@csrf_exempt
def handle_paypal_ipn(request):
    if request.method == 'POST' and request.POST:
        try:
            payment_date_raw = request.POST.get('payment_date', '')
            payment_date = strtotime(payment_date_raw) if payment_date_raw else None

            transaccion = TransaccionPaypal(
                payer_id=request.POST.get('payer_id', ''),
                payment_date=payment_date,
                payment_status=request.POST.get('payment_status', ''),
                quantity=request.POST.get('quantity', '1'),
                invoice=request.POST.get('invoice', ''),
                first_name=request.POST.get('first_name', ''),
                payer_status=request.POST.get('payer_status', ''),
                payer_email=request.POST.get('payer_email', ''),
                txn_id=request.POST.get('txn_id', ''),
                receiver_id=request.POST.get('receiver_id', ''),
                payment_gross=request.POST.get('payment_gross', '0.00'),
                custom=request.POST.get('custom', '')
            )
            transaccion.save()
            return HttpResponse("OK", status=200)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al guardar la transacción: {str(e)}")
            return HttpResponse("Error", status=500)
    
    return HttpResponse("Bad Request", status=400)

def strtotime(i_time: str):
    '''formatearemos el tiempo de paypal a una salida de formato linux'''
    i_time_space = i_time.split(" ")
    meses = "Jan_Feb_Mar_Apr_May_Jun_Jul_Aug_Sep_Oct_Nov_Dec".split("_")
    year = i_time_space[3]
    month = i_time_space[1]
    day = i_time_space[2].replace(',', '')
    hora = i_time_space[0].split(":")[0]
    min = i_time_space[0].split(":")[1]
    seg = i_time_space[0].split(":")[2]
    return datetime(int(year), int(meses.index(month)) + 1, int(day), int(hora), int(min), int(seg))

def get_cart_count(request):
    """
    Vista para obtener el contador del carrito vía AJAX
    """
    cart = get_or_create_cart(request)
    cart_count = sum(item.quantity for item in cart.cartitem_set.all())
    return JsonResponse({'cart_count': cart_count})

def generate_order_number():
    """Genera un número de orden único"""
    import random
    import string
    from datetime import datetime
    
    # Formato: ORD-YYYYMMDD-XXXX (ORD-20250628-A1B2)
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ORD-{date_str}-{random_str}"

def create_order_from_cart(user, cart, shipping_info, delivery_info=None):
    """
    Crea una orden a partir del carrito de compras
    """
    cart_items = cart.cartitem_set.all()
    
    if not cart_items:
        return None
    
    # Calcular total de productos
    subtotal = sum(item.total_price() for item in cart_items)
    
    # Obtener información de entrega
    if delivery_info is None:
        delivery_info = {
            'delivery_method': 'pickup',
            'delivery_cost': 0
        }
    
    delivery_cost = Decimal(str(delivery_info.get('delivery_cost', 0)))
    total_amount = Decimal(str(subtotal)) + delivery_cost
    
    # Preparar información de envío según el método
    delivery_method = delivery_info.get('delivery_method', 'pickup')
    if delivery_method == 'delivery':
        shipping_address = delivery_info.get('shipping_address', '')
        shipping_city = delivery_info.get('shipping_city', '')
        shipping_phone = delivery_info.get('shipping_phone', '')
    else:
        # Para retiro en tienda
        pickup_store = delivery_info.get('pickup_store', 'main_store')
        store_addresses = {
            'main_store': 'Tienda Principal - Av. Providencia 1234, Providencia',
            'mall_store': 'Sucursal Mall - Centro Comercial Plaza, Local 234',
            'norte_store': 'Sucursal Norte - Av. Independencia 567, Independencia',
        }
        shipping_address = f"RETIRO EN TIENDA: {store_addresses.get(pickup_store, 'Tienda Principal')}"
        shipping_city = 'Santiago'
        shipping_phone = user.phone if hasattr(user, 'phone') and user.phone else 'No especificado'
    
    # Crear la orden
    order = Order.objects.create(
        user=user,
        order_number=generate_order_number(),
        total_amount=total_amount,
        delivery_method=delivery_method,
        delivery_cost=delivery_cost,
        shipping_address=shipping_address,
        shipping_city=shipping_city,
        shipping_phone=shipping_phone,
        notes=delivery_info.get('special_instructions', ''),
    )
    
    # Crear los items de la orden
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=Decimal(str(cart_item.product.price))
        )
    
    # Limpiar el carrito
    cart_items.delete()
    
    return order

# Vistas para el historial de órdenes

@login_required
def user_order_history(request):
    """Vista para que los usuarios vean su historial de compras"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
        'user': request.user
    }
    return render(request, 'profile/order-history.html', context)

@login_required
def order_detail(request, order_id):
    """Vista para ver detalles de una orden específica"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'order_items': order.items.all()
    }
    return render(request, 'profile/order-detail.html', context)

@require_http_methods(["POST"])
def update_delivery_info(request):
    """Vista para actualizar información de entrega via AJAX"""
    try:
        delivery_method = request.POST.get('delivery_method', 'pickup')
        delivery_cost = 0
        
        if delivery_method == 'delivery':
            delivery_cost = 3000  # $3.000 por delivery
        
        # Guardar en la sesión
        delivery_info = {
            'delivery_method': delivery_method,
            'delivery_cost': delivery_cost,
        }
        
        # Agregar campos específicos según el método
        if delivery_method == 'delivery':
            delivery_info.update({
                'shipping_address': request.POST.get('shipping_address', ''),
                'shipping_city': request.POST.get('shipping_city', ''),
                'shipping_phone': request.POST.get('shipping_phone', ''),
            })
        else:
            delivery_info.update({
                'pickup_store': request.POST.get('pickup_store', 'main_store'),
            })
        
        delivery_info['special_instructions'] = request.POST.get('special_instructions', '')
        
        request.session['delivery_info'] = delivery_info
        
        # Calcular nuevo total
        cart = get_or_create_cart(request)
        cart_items = cart.cartitem_set.all()
        subtotal = sum(item.total_price() for item in cart_items)
        total_with_delivery = subtotal + delivery_cost
        
        return JsonResponse({
            'success': True,
            'delivery_cost': delivery_cost,
            'total_with_delivery': total_with_delivery,
            'message': 'Información de entrega actualizada'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)