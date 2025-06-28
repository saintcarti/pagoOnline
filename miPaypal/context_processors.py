from .models import Cart, CartItem

def cart_context(request):
    """
    Procesador de contexto para proporcionar información del carrito
    en todas las plantillas.
    """
    cart_count = 0
    
    try:
        if request.user.is_authenticated:
            # Usuario autenticado: buscar carrito por usuario
            cart = Cart.objects.filter(user=request.user).first()
        else:
            # Usuario anónimo: buscar carrito por session_key
            if request.session.session_key:
                cart = Cart.objects.filter(session_key=request.session.session_key).first()
            else:
                cart = None
        
        if cart:
            # Calcular el número total de productos en el carrito
            cart_count = sum(item.quantity for item in cart.cartitem_set.all())
    
    except Exception:
        # En caso de error, establecer cart_count a 0
        cart_count = 0
    
    return {
        'cart_count': cart_count
    }
