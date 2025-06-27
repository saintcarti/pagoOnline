# views.py
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .models import Product, TransaccionPaypal, Cart, CartItem
from datetime import datetime
from .customButton import CustomPaypalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

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
    
    return redirect('view_cart')

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
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'paypal/cart.html', context)

def checkout(request):
    cart = get_or_create_cart(request)
    cart_items = cart.cartitem_set.all()
    
    if not cart_items:
        return redirect('view_cart')
    
    total = sum(item.total_price() for item in cart_items)
    item_names = ", ".join([item.product.name for item in cart_items])
    
    host = request.get_host()
    paypal_checkout = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': total,
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
        'paypal': paypal_payment
    }
    return render(request, 'paypal/checkout.html', context)

def payment_successful(request):
    cart = get_or_create_cart(request)
    cart_items = cart.cartitem_set.all()
    
    # Limpiar el carrito después de una compra exitosa
    cart_items.delete()
    cart.delete()
    
    return render(request, 'paypal/payment-success.html', {'cart_items': cart_items})

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