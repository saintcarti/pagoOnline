from django.shortcuts import render, redirect, get_object_or_404
from miPaypal.models import Product, CustomUser, Brand, Category, ContactMessage, Order, OrderItem, StockMovement
from miPaypal.forms import ProductForm, CustomUserCreationForm, StaffRegistrationForm, UserEditForm, ManualOrderForm, OrderStatusUpdateForm, OrderItemForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from miPaypal.decorators import admin_required, role_required
from django.core.paginator import Paginator
from django.db.models import Q 
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.utils import timezone

# Create your views here.
def index(request):
    product = Product.objects.all()

    return render(request,'ecommerce/index.html',{"products":product})

def custom_logout(request):
    logout(request)
    return redirect('index-page')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').lower().strip()  # Convertir a minúsculas y limpiar espacios
        password = request.POST.get('password')
        
        # Intentar encontrar el usuario de forma case-insensitive
        try:
            # Buscar usuario por username en minúsculas
            user_obj = CustomUser.objects.get(username__iexact=username)
            # Autenticar con el username real del usuario
            user = authenticate(request, username=user_obj.username, password=password)
        except CustomUser.DoesNotExist:
            user = None
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
            
            # Verificar si hay un redirect 'next'
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            # Redirigir al dashboard si es staff, sino al índice
            if user.is_staff:
                return redirect('dashboard-panel-page')
            else:
                return redirect('index-page')
        else:
            error_message = 'Usuario o contraseña incorrectos'
            return render(request, 'auth/login.html', {'error': error_message})
    
    return render(request, 'auth/login.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.rol = 'cliente'  # Asignamos automáticamente el rol de cliente
            user.save()
            
            # Autenticar al usuario después del registro
            auth_login(request, user)
            messages.success(request, 'Registro exitoso!')
            return redirect('index-page')
        else:
            # Pasar los errores del formulario al template
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})


def products(request):
    # Obtener parámetros de filtro
    category_id = request.GET.get('category')
    brand_id = request.GET.get('brand')
    search_query = request.GET.get('search')
    
    # Obtener todos los productos
    product_list = Product.objects.all().order_by('-id')
    
    # Aplicar filtros
    current_category = None
    current_brand = None
    
    if category_id:
        try:
            current_category = Category.objects.get(id=category_id)
            product_list = product_list.filter(categories=current_category)
        except Category.DoesNotExist:
            pass
    
    if brand_id:
        try:
            current_brand = Brand.objects.get(id=brand_id)
            product_list = product_list.filter(brand=current_brand)
        except Brand.DoesNotExist:
            pass
    
    if search_query:
        product_list = product_list.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Configurar paginación - 12 productos por página
    paginator = Paginator(product_list, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # Obtener todas las categorías y marcas para los filtros
    categories = Category.objects.all()
    brands = Brand.objects.all()

    return render(request,'ecommerce/products.html',{
        "products": products,
        "categories": categories,
        "brands": brands,
        "current_category": current_category,
        "current_brand": current_brand,
        "search_query": search_query or '',
    })

def about(request):
    return render(request,'ecommerce/about.html')

def contact_view(request):
    # Datos iniciales
    context = {
        'form_data': {
            'name': '',
            'email': '',
            'phone': '',
            'reason': '',
            'message': ''
        },
        'form_errors': {},
        'form_submitted': False
    }

    if request.method == 'POST':
        # Recoger datos del formulario
        form_data = {
            'name': request.POST.get('name', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'phone': request.POST.get('phone', '').strip(),
            'reason': request.POST.get('reason', '').strip(),
            'message': request.POST.get('message', '').strip()
        }
        
        # Validación
        errors = {}
        
        if not form_data['name']:
            errors['name'] = 'Este campo es obligatorio.'
            
        if not form_data['email'] or '@' not in form_data['email']:
            errors['email'] = 'Ingrese un correo electrónico válido.'
            
        if not form_data['phone'].isdigit() or len(form_data['phone']) not in [9, 10]:
            errors['phone'] = 'El teléfono debe tener 9 o 10 dígitos.'
            
        if not form_data['reason']:
            errors['reason'] = 'Seleccione un motivo de contacto.'
            
        if not form_data['message']:
            errors['message'] = 'Por favor escriba su mensaje.'
        
        if errors:
            # Si hay errores, mostramos el formulario nuevamente
            context.update({
                'form_data': form_data,
                'form_errors': errors
            })
        else:
            # Guardar el mensaje en la base de datos
            contact_message = ContactMessage.objects.create(
                name=form_data['name'],
                email=form_data['email'],
                phone=form_data['phone'],
                reason=form_data['reason'],
                message=form_data['message']
            )
            
            # Mostrar la página de éxito directamente sin redirigir
            context.update({
                'form_submitted': True,
                'form_data': form_data,
                'message_id': contact_message.id  # Para referencia
            })
    
    return render(request, 'ecommerce/contact.html', context)

@admin_required
@admin_required
def admin_settings(request):
    """Vista para configuraciones del sistema"""
    # Obtener estadísticas básicas
    total_products = Product.objects.count()
    total_users = CustomUser.objects.count()
    total_messages = ContactMessage.objects.count()
    
    context = {
        'total_products': total_products,
        'total_users': total_users,
        'total_messages': total_messages,
    }
    
    return render(request, 'dashboard-panel/profile/admin-settings.html', context)

@admin_required
def admin_profile(request):
    """Vista para ver y editar el perfil del administrador"""
    if request.method == 'POST':
        # Actualizar información del usuario
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.telefono = request.POST.get('telefono', '')
        user.rut = request.POST.get('rut', '')
        user.direccion = request.POST.get('direccion', '')
        
        # Manejar imagen de perfil (si se implementa más tarde)
        # if 'profile_image' in request.FILES:
        #     user.profile_image = request.FILES['profile_image']
        
        user.save()
        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('admin-profile-page')
    
    # Obtener estadísticas del usuario
    messages_attended = 0
    if hasattr(request.user, 'contactmessage_set'):
        messages_attended = ContactMessage.objects.filter(attended_by=request.user).count()
    
    context = {
        'messages_attended': messages_attended,
    }
    
    return render(request, 'dashboard-panel/profile/admin-profile.html', context)

@admin_required
def dashboard(request):
    """Vista para el dashboard con estadísticas"""
    from django.db.models import Count
    from datetime import datetime, timedelta
    
    # Estadísticas generales
    total_products = Product.objects.count()
    total_users = CustomUser.objects.count()
    total_messages = ContactMessage.objects.count()
    pending_messages = ContactMessage.objects.filter(status='pendiente').count()
    
    # Mensajes por estado
    messages_by_status = ContactMessage.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Mensajes recientes (últimos 7 días)
    week_ago = datetime.now() - timedelta(days=7)
    recent_messages = ContactMessage.objects.filter(
        created_at__gte=week_ago
    ).order_by('-created_at')[:5]
    
    context = {
        'total_products': total_products,
        'total_users': total_users,
        'total_messages': total_messages,
        'pending_messages': pending_messages,
        'messages_by_status': messages_by_status,
        'recent_messages': recent_messages,
    }
    
    return render(request, 'dashboard-panel/dashboard.html', context)

@admin_required
def list_products(request):
    # Obtener parámetros de filtro
    category_id = request.GET.get('category')
    brand_id = request.GET.get('brand')
    search_query = request.GET.get('search')
    page_number = request.GET.get('page')
    
    # Obtener todos los productos
    products = Product.objects.all().order_by('-id')
    
    # Aplicar filtros
    current_category = None
    current_brand = None
    
    if category_id:
        try:
            current_category = Category.objects.get(id=category_id)
            products = products.filter(categories=current_category)
        except Category.DoesNotExist:
            pass
    
    if brand_id:
        try:
            current_brand = Brand.objects.get(id=brand_id)
            products = products.filter(brand=current_brand)
        except Brand.DoesNotExist:
            pass
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(products, 10)
    page_obj = paginator.get_page(page_number)
    
    # Obtener todas las categorías y marcas para los filtros
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    return render(request, 'dashboard-panel/crud-products/list-product.html', {
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'current_category': current_category,
        'current_brand': current_brand,
        'search_query': search_query or '',
    })


@admin_required
def crear_pview(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.POST.get('image')
        brand_id = request.POST.get('brand')
        categories_ids = request.POST.getlist('categories')

        # Crear el producto
        product = Product(name=name, price=price, description=description, image=image)
        
        # Asignar la marca si se seleccionó una
        if brand_id:
            try:
                brand = Brand.objects.get(id=brand_id)
                product.brand = brand
            except Brand.DoesNotExist:
                pass
        
        product.save()
        
        # Asignar las categorías después de guardar
        if categories_ids:
            categories = Category.objects.filter(id__in=categories_ids)
            product.categories.set(categories)

        return redirect('list-products')

    # Pasar las marcas y categorías al template
    brands = Brand.objects.all()
    categories = Category.objects.all()
    return render(request, 'dashboard-panel/crud-products/create-product.html', {
        'brands': brands,
        'categories': categories
    })

@admin_required
def delete_product(request, pk):
    """Vista para eliminar productos"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f'Producto {product.name} eliminado correctamente')
        return redirect('list-products')
    return render(request, 'dashboard-panel/crud-products/confirm-delete.html', {'product': product})


@admin_required
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('list-products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'dashboard-panel/crud-products/update-product.html', {
        'form': form,
        'product': product
    })

@admin_required
def staff_register(request):
    """Vista para registrar nuevos usuarios (solo admin)"""
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario {user.username} creado exitosamente!')
            return redirect('list-user')  # Cambiado a 'list-user' para consistencia
    else:
        form = StaffRegistrationForm()
    
    return render(request, 'dashboard-panel/crud-users/create-user.html', {'form': form})

@admin_required
def list_user(request):
    """Vista unificada para listar usuarios con filtros y paginación"""
    role_filter = request.GET.get('role')
    search_query = request.GET.get('search')
    page_number = request.GET.get('page')
    per_page = request.GET.get('per_page', '10')  # Por defecto 10 usuarios por página
    
    # Validar per_page
    try:
        per_page = int(per_page)
        if per_page not in [5, 10, 25, 50]:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10
    
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Aplicar filtros
    if role_filter:
        users = users.filter(rol=role_filter)
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(rut__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(users, per_page)
    page_obj = paginator.get_page(page_number)
    
    # Pasar los roles definidos en el modelo al template
    return render(request, 'dashboard-panel/crud-users/list-user.html', {
        'page_obj': page_obj,
        'current_role': role_filter,
        'search_query': search_query or '',
        'per_page': per_page,
        'user_roles': CustomUser.ROLES
    })

@admin_required
def delete_user(request, user_id):
    """Vista para eliminar usuarios"""
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuario {username} eliminado correctamente')
        return redirect('list-user')  # Cambiado a 'list-user' para consistencia
    return render(request, 'dashboard-panel/crud-users/confirm-delete.html', {'user': user})

@admin_required
def edit_user(request, user_id):
    """Vista para editar usuarios existentes"""
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente')
            return redirect('list-user')  # Cambiado a 'list-user' para consistencia
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'dashboard-panel/crud-users/edit-user.html', {'form': form})

@admin_required
def product_detail(request, pk):
    """Vista para mostrar los detalles completos de un producto"""
    product = get_object_or_404(Product, pk=pk)
    
    # Obtener productos relacionados (misma marca o categorías similares)
    related_products = Product.objects.filter(
        Q(brand=product.brand) | 
        Q(categories__in=product.categories.all())
    ).exclude(pk=product.pk).distinct()[:4]
    
    return render(request, 'dashboard-panel/crud-products/product-detail.html', {
        'product': product,
        'related_products': related_products
    })

@admin_required
def list_contact_messages(request):
    """Vista para listar mensajes de contacto en el dashboard del admin"""
    status_filter = request.GET.get('status')
    reason_filter = request.GET.get('reason')
    search_query = request.GET.get('search')
    page_number = request.GET.get('page')
    
    messages_list = ContactMessage.objects.all().order_by('-created_at')
    
    # Aplicar filtros
    if status_filter:
        messages_list = messages_list.filter(status=status_filter)
    
    if reason_filter:
        messages_list = messages_list.filter(reason=reason_filter)
    
    if search_query:
        messages_list = messages_list.filter(
            Q(name__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(messages_list, 10)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboard-panel/crud-messages/list-messages.html', {
        'page_obj': page_obj,
        'current_status': status_filter,
        'current_reason': reason_filter,
        'search_query': search_query or '',
        'status_choices': ContactMessage.STATUS_CHOICES,
        'reason_choices': ContactMessage.REASON_CHOICES,
    })

@admin_required
def view_contact_message(request, message_id):
    """Vista para ver un mensaje de contacto específico"""
    message = get_object_or_404(ContactMessage, id=message_id)
    
    if request.method == 'POST':
        # Actualizar estado y respuesta
        new_status = request.POST.get('status')
        response = request.POST.get('response')
        
        if new_status:
            message.status = new_status
        if response:
            message.response = response
        
        message.attended_by = request.user
        message.save()
        
        messages.success(request, 'Mensaje actualizado correctamente')
        return redirect('view-contact-message', message_id=message.id)
    
    return render(request, 'dashboard-panel/crud-messages/view-message.html', {
        'message': message,
        'status_choices': ContactMessage.STATUS_CHOICES,
    })

@admin_required
def delete_contact_message(request, message_id):
    """Vista para eliminar un mensaje de contacto"""
    message = get_object_or_404(ContactMessage, id=message_id)
    
    if request.method == 'POST':
        message_name = message.name
        message.delete()
        messages.success(request, f'Mensaje de {message_name} eliminado correctamente')
        return redirect('list-contact-messages')
    
    return render(request, 'dashboard-panel/crud-messages/confirm-delete-message.html', {
        'message': message
    })

@admin_required
def change_password(request):
    """Vista para cambiar la contraseña del usuario"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        user = request.user
        
        # Verificar contraseña actual
        if not user.check_password(old_password):
            messages.error(request, 'La contraseña actual es incorrecta')
            return redirect('admin-profile-page')
        
        # Verificar que las nuevas contraseñas coincidan
        if new_password1 != new_password2:
            messages.error(request, 'Las nuevas contraseñas no coinciden')
            return redirect('admin-profile-page')
        
        # Verificar longitud mínima
        if len(new_password1) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
            return redirect('admin-profile-page')
        
        # Cambiar contraseña
        user.set_password(new_password1)
        user.save()
        
        # Actualizar sesión para mantener al usuario logueado
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        
        messages.success(request, 'Contraseña cambiada correctamente')
        return redirect('admin-profile-page')
    
    return redirect('admin-profile-page')

@login_required
def user_profile(request):
    """Vista para ver y editar el perfil del usuario regular"""
    if request.method == 'POST':
        # Actualizar información del usuario
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.telefono = request.POST.get('telefono', '')
        user.rut = request.POST.get('rut', '')
        user.direccion = request.POST.get('direccion', '')
        
        # Manejar imagen de perfil (si se implementa más tarde)
        # if 'profile_image' in request.FILES:
        #     user.profile_image = request.FILES['profile_image']
        
        user.save()
        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('user-profile-page')
    
    # Obtener estadísticas del usuario (mensajes enviados)
    user_messages_count = 0
    if hasattr(ContactMessage, 'objects'):
        user_messages_count = ContactMessage.objects.filter(email=request.user.email).count()
    
    context = {
        'user_messages_count': user_messages_count,
    }
    
    return render(request, 'profile/user-profile.html', context)

@login_required
def user_change_password(request):
    """Vista para cambiar la contraseña del usuario regular"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        user = request.user
        
        # Verificar contraseña actual
        if not user.check_password(old_password):
            messages.error(request, 'La contraseña actual es incorrecta')
            return redirect('user-profile-page')
        
        # Verificar que las nuevas contraseñas coincidan
        if new_password1 != new_password2:
            messages.error(request, 'Las nuevas contraseñas no coinciden')
            return redirect('user-profile-page')
        
        # Verificar longitud mínima
        if len(new_password1) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
            return redirect('user-profile-page')
        
        # Cambiar contraseña
        user.set_password(new_password1)
        user.save()
        
        # Actualizar sesión para mantener al usuario logueado
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        
        messages.success(request, 'Contraseña cambiada correctamente')
        return redirect('user-profile-page')
    
    return redirect('user-profile-page')

@staff_member_required
def view_user_detail(request, user_id):
    """Vista para ver los detalles completos de un usuario"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Obtener estadísticas del usuario
    user_messages_count = 0
    if hasattr(ContactMessage, 'objects'):
        user_messages_count = ContactMessage.objects.filter(email=user.email).count()
    
    # Obtener información adicional
    context = {
        'user_detail': user,
        'user_messages_count': user_messages_count,
        'last_login_formatted': user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Nunca',
        'date_joined_formatted': user.date_joined.strftime('%d/%m/%Y %H:%M'),
    }
    
    return render(request, 'dashboard-panel/crud-users/view-user.html', context)

# Vistas para gestión de órdenes por administradores

@role_required('contador')
def list_orders(request):
    """Vista para que los administradores y contadores vean todas las órdenes"""
    # Obtener parámetros de filtro
    status_filter = request.GET.get('status')
    payment_filter = request.GET.get('payment_status')
    search_query = request.GET.get('search')
    
    # Obtener todas las órdenes
    orders_list = Order.objects.all().order_by('-created_at')
    
    # Aplicar filtros
    if status_filter:
        orders_list = orders_list.filter(order_status=status_filter)
    
    if payment_filter:
        orders_list = orders_list.filter(payment_status=payment_filter)
    
    if search_query:
        orders_list = orders_list.filter(
            Q(order_number__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    # Configurar paginación - 20 órdenes por página
    paginator = Paginator(orders_list, 20)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {
        'orders': orders,
        'status_choices': Order.ORDER_STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
        'current_status': status_filter,
        'current_payment_status': payment_filter,
        'search_query': search_query or '',
    }
    
    return render(request, 'dashboard-panel/crud-orders/list-orders.html', context)

@role_required('contador')
def order_detail_admin(request, order_id):
    """Vista para que los administradores y contadores vean detalles de una orden"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # Actualizar estado de la orden
        new_status = request.POST.get('order_status')
        new_payment_status = request.POST.get('payment_status')
        
        if new_status:
            order.order_status = new_status
        if new_payment_status:
            order.payment_status = new_payment_status
            
        order.save()
        messages.success(request, 'Estado de la orden actualizado correctamente.')
        return redirect('order-detail-admin', order_id=order.id)
    
    context = {
        'order': order,
        'order_items': order.items.all(),
        'status_choices': Order.ORDER_STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
    }
    
    return render(request, 'dashboard-panel/crud-orders/order-detail.html', context)


@login_required
def vista_bodega(request):
    """Vista de bodega para vendedores - muestra productos con información de stock"""
    
    # Verificar que el usuario sea vendedor, bodeguero o staff
    if not (request.user.is_staff or request.user.rol in ['vendedor', 'bodeguero']):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('index-page')
    
    # Obtener parámetros de filtrado
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    brand_filter = request.GET.get('brand', '')
    stock_filter = request.GET.get('stock_status', '')
    
    # Base queryset
    products = Product.objects.all().select_related('brand').prefetch_related('categories')
    
    # Aplicar filtros
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if category_filter:
        products = products.filter(categories__id=category_filter)
    
    if brand_filter:
        products = products.filter(brand__id=brand_filter)
    
    if stock_filter:
        if stock_filter == 'sin_stock':
            products = products.filter(stock=0)
        elif stock_filter == 'stock_bajo':
            products = products.filter(stock__gt=0, stock__lte=5)
        elif stock_filter == 'stock_medio':
            products = products.filter(stock__gt=5, stock__lte=20)
        elif stock_filter == 'stock_alto':
            products = products.filter(stock__gt=20)
    
    # Ordenar por stock (productos sin stock primero, luego por stock ascendente)
    products = products.extra(
        select={'stock_zero': 'CASE WHEN stock = 0 THEN 1 ELSE 0 END'}
    ).order_by('-stock_zero', 'stock', 'name')
    
    # Paginación
    paginator = Paginator(products, 20)  # 20 productos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas rápidas
    total_products = Product.objects.count()
    sin_stock = Product.objects.filter(stock=0).count()
    stock_bajo = Product.objects.filter(stock__gt=0, stock__lte=5).count()
    stock_medio = Product.objects.filter(stock__gt=5, stock__lte=20).count()
    stock_alto = Product.objects.filter(stock__gt=20).count()
    
    # Obtener opciones para filtros
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'brand_filter': brand_filter,
        'stock_filter': stock_filter,
        'categories': categories,
        'brands': brands,
        'stats': {
            'total_products': total_products,
            'sin_stock': sin_stock,
            'stock_bajo': stock_bajo,
            'stock_medio': stock_medio,
            'stock_alto': stock_alto,
        }
    }
    
    return render(request, 'dashboard-panel/bodega/vista-bodega.html', context)


@login_required  
def actualizar_stock(request, product_id):
    """Vista para actualizar rápidamente el stock de un producto"""
    
    # Verificar permisos
    if not (request.user.is_staff or request.user.rol in ['vendedor', 'bodeguero']):
        messages.error(request, 'No tienes permisos para actualizar stock.')
        return redirect('vista-bodega')
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            nuevo_stock = int(request.POST.get('stock', 0))
            if nuevo_stock < 0:
                messages.error(request, 'El stock no puede ser negativo.')
            else:
                stock_anterior = product.stock
                
                # Determinar tipo de movimiento
                if nuevo_stock > stock_anterior:
                    movement_type = 'entrada'
                    reason = 'reabastecimiento'
                    quantity = nuevo_stock - stock_anterior
                elif nuevo_stock < stock_anterior:
                    movement_type = 'ajuste'
                    reason = 'inventario'
                    quantity = stock_anterior - nuevo_stock
                else:
                    # No hay cambio
                    messages.info(request, 'El stock no ha cambiado.')
                    return redirect('vista-bodega')
                
                # Actualizar stock y registrar movimiento
                product.stock = nuevo_stock
                product.save()
                
                # Registrar movimiento de stock
                StockMovement.register_movement(
                    product=product,
                    movement_type=movement_type,
                    reason=reason,
                    quantity=quantity,
                    user=request.user,
                    notes=f"Actualización manual de stock desde vista de bodega"
                )
                
                messages.success(request, 
                    f'Stock de "{product.name}" actualizado de {stock_anterior} a {nuevo_stock} unidades.')
                
        except ValueError:
            messages.error(request, 'Por favor ingresa un número válido.')
    
    return redirect('vista-bodega')


# Vistas para gestión de órdenes por vendedores

@login_required
def lista_ordenes_vendedor(request):
    """Vista para que vendedores vean sus órdenes"""
    
    # Verificar permisos
    if not (request.user.is_staff or request.user.rol == 'vendedor'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('index-page')
    
    # Filtros
    status_filter = request.GET.get('status', '')
    payment_filter = request.GET.get('payment', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset - vendedores ven solo sus órdenes, admins ven todas
    if request.user.is_staff:
        orders = Order.objects.all().select_related('user', 'created_by')
    else:
        orders = Order.objects.filter(created_by=request.user).select_related('user', 'created_by')
    
    # Aplicar filtros
    if status_filter:
        orders = orders.filter(order_status=status_filter)
    
    if payment_filter:
        orders = orders.filter(payment_status=payment_filter)
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Ordenar por fecha de creación (más recientes primero)
    orders = orders.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_orders = orders.count()
    pending_orders = orders.filter(order_status='pending').count()
    shipped_orders = orders.filter(order_status='shipped').count()
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
        'search_query': search_query,
        'order_status_choices': Order.ORDER_STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
        'stats': {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'shipped_orders': shipped_orders,
        }
    }
    
    return render(request, 'dashboard-panel/ordenes-vendedor/lista-ordenes.html', context)


@login_required
def crear_orden_manual(request):
    """Vista para crear órdenes manuales"""
    
    # Verificar permisos
    if not (request.user.is_staff or request.user.rol == 'vendedor'):
        messages.error(request, 'No tienes permisos para crear órdenes.')
        return redirect('index-page')
    
    if request.method == 'POST':
        form = ManualOrderForm(request.POST)
        order_items_json = request.POST.get('order_items')
        
        if form.is_valid() and order_items_json:
            try:
                import json
                order_items = json.loads(order_items_json)
                
                if not order_items:
                    messages.error(request, 'Debe agregar al menos un producto a la orden.')
                    raise ValueError("No items in order")
                
                orden = form.save(commit=False)
                
                # Generar número de orden único
                import random
                import string
                while True:
                    order_number = 'ORD-' + ''.join(random.choices(string.digits, k=8))
                    if not Order.objects.filter(order_number=order_number).exists():
                        break
                
                orden.order_number = order_number
                orden.created_by = request.user
                
                # Calcular total y crear items
                total_amount = 0
                with transaction.atomic():
                    orden.save()
                    
                    for item_data in order_items:
                        product = Product.objects.get(id=item_data['product_id'])
                        quantity = int(item_data['quantity'])
                        
                        # Verificar stock disponible
                        if product.stock < quantity:
                            raise ValueError(f"Stock insuficiente para {product.name}")
                        
                        # Crear el item de la orden
                        OrderItem.objects.create(
                            order=orden,
                            product=product,
                            quantity=quantity,
                            price=product.price
                        )
                        
                        # Actualizar stock
                        product.stock -= quantity
                        product.save()
                        
                        total_amount += product.price * quantity
                    
                    # Actualizar el total de la orden
                    orden.total_amount = total_amount
                    orden.save()
                
                messages.success(request, f'Orden #{orden.order_number} creada exitosamente.')
                return redirect('detalle-orden-vendedor', order_id=orden.id)
                
            except (json.JSONDecodeError, ValueError, Product.DoesNotExist) as e:
                messages.error(request, f'Error al crear la orden: {str(e)}')
        else:
            if not order_items_json:
                messages.error(request, 'Debe agregar al menos un producto a la orden.')
    else:
        form = ManualOrderForm()
    
    # Obtener productos disponibles con stock
    productos = Product.objects.filter(stock__gt=0).select_related('brand').prefetch_related('categories')
    
    context = {
        'form': form,
        'productos': productos,
        'title': 'Crear Nueva Orden',
    }
    
    return render(request, 'dashboard-panel/ordenes-vendedor/crear-orden.html', context)


@login_required
def detalle_orden_vendedor(request, order_id):
    """Vista de detalle de orden para vendedores"""
    
    # Verificar permisos
    if not (request.user.is_staff or request.user.rol == 'vendedor'):
        messages.error(request, 'No tienes permisos para ver esta orden.')
        return redirect('index-page')
    
    # Obtener la orden
    if request.user.is_staff:
        orden = get_object_or_404(Order, id=order_id)
    else:
        orden = get_object_or_404(Order, id=order_id, created_by=request.user)
    
    # Procesar formulario de actualización de estado
    if request.method == 'POST':
        if 'update_status' in request.POST:
            status_form = OrderStatusUpdateForm(request.POST, instance=orden)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, 'Estado de la orden actualizado correctamente.')
                return redirect('detalle-orden-vendedor', order_id=orden.id)
        
        elif 'add_item' in request.POST:
            item_form = OrderItemForm(request.POST)
            if item_form.is_valid():
                item = item_form.save(commit=False)
                item.order = orden
                
                # Verificar stock disponible
                if item.product.stock >= item.quantity:
                    # Reducir stock
                    item.product.stock -= item.quantity
                    item.product.save()
                    
                    item.save()
                    
                    # Recalcular total de la orden
                    orden.total_amount = sum(
                        item.quantity * item.price 
                        for item in orden.items.all()
                    )
                    orden.save()
                    
                    messages.success(request, f'Producto "{item.product.name}" agregado a la orden.')
                else:
                    messages.error(request, f'Stock insuficiente. Solo hay {item.product.stock} unidades disponibles.')
                
                return redirect('detalle-orden-vendedor', order_id=orden.id)
    
    # Formularios
    status_form = OrderStatusUpdateForm(instance=orden)
    item_form = OrderItemForm()
    
    context = {
        'order': orden,
        'order_items': orden.items.all(),
        'status_form': status_form,
        'item_form': item_form,
    }
    
    return render(request, 'dashboard-panel/ordenes-vendedor/detalle-orden.html', context)


@login_required
def eliminar_item_orden(request, order_id, item_id):
    """Eliminar un item de una orden"""
    
    # Verificar permisos
    if not (request.user.is_staff or request.user.rol == 'vendedor'):
        messages.error(request, 'No tienes permisos para modificar órdenes.')
        return redirect('index-page')
    
    # Obtener la orden y el item
    if request.user.is_staff:
        orden = get_object_or_404(Order, id=order_id)
    else:
        orden = get_object_or_404(Order, id=order_id, created_by=request.user)
    
    item = get_object_or_404(OrderItem, id=item_id, order=orden)
    
    if request.method == 'POST':
        # Restaurar stock
        item.product.stock += item.quantity
        item.product.save()
        
        # Eliminar item
        product_name = item.product.name
        item.delete()
        
        # Recalcular total de la orden
        orden.total_amount = sum(
            item.quantity * item.price 
            for item in orden.items.all()
        )
        orden.save()
        
        messages.success(request, f'Producto "{product_name}" eliminado de la orden.')
    
    return redirect('detalle-orden-vendedor', order_id=orden.id)

# Vistas específicas para bodegueros

@login_required
def dashboard_bodeguero(request):
    """Dashboard principal para bodegueros"""
    
    # Verificar que el usuario sea bodeguero o staff
    if not (request.user.is_staff or request.user.rol == 'bodeguero'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('index-page')
    
    # Obtener estadísticas de inventario
    todos_productos = Product.objects.all().select_related('brand')
    productos_criticos = todos_productos.filter(stock__lte=5).order_by('stock')[:10]
    
    # Calcular estadísticas
    from datetime import datetime, timedelta
    hoy = datetime.now().date()
    
    # Movimientos del día
    movimientos_hoy = StockMovement.objects.filter(created_at__date=hoy).count()
    
    stats = {
        'total_products': todos_productos.count(),
        'total_stock': sum(p.stock for p in todos_productos),
        'productos_disponibles': todos_productos.filter(stock__gt=0).count(),
        'sin_stock': todos_productos.filter(stock=0).count(),
        'stock_bajo': todos_productos.filter(stock__gt=0, stock__lte=5).count(),
        'alertas_stock': todos_productos.filter(stock__lte=5).count(),
        'valor_total_inventario': sum(p.price * p.stock for p in todos_productos),
        'movimientos_hoy': movimientos_hoy
    }
    
    # Obtener productos más vendidos (basado en OrderItems)
    from django.db.models import Sum, F
    productos_top = OrderItem.objects.values(
        'product__name', 'product__brand__name', 'product__stock'
    ).annotate(
        total_vendido=Sum('quantity'),
        ingresos_totales=Sum(F('quantity') * F('price'))
    ).order_by('-total_vendido')[:10]
    
    context = {
        'stats': stats,
        'productos_criticos': productos_criticos,
        'productos_top': productos_top,
        'todos_productos': todos_productos,
    }
    
    return render(request, 'dashboard-panel/bodega/dashboard-bodeguero.html', context)


@login_required
def ajuste_stock_masivo(request):
    """Vista para ajustes masivos de stock"""
    
    # Verificar permisos
    if not (request.user.is_staff or request.user.rol == 'bodeguero'):
        messages.error(request, 'No tienes permisos para realizar ajustes de stock.')
        return redirect('dashboard-bodeguero')
    
    if request.method == 'POST':
        productos_ids = request.POST.getlist('productos')
        tipo_ajuste = request.POST.get('tipo_ajuste')
        cantidad = int(request.POST.get('cantidad', 0))
        motivo = request.POST.get('motivo')
        notas = request.POST.get('notas', '')
        
        if not productos_ids:
            messages.error(request, 'Debes seleccionar al menos un producto.')
            return redirect('dashboard-bodeguero')
        
        productos_actualizados = 0
        
        try:
            with transaction.atomic():
                for producto_id in productos_ids:
                    producto = Product.objects.get(id=producto_id)
                    stock_anterior = producto.stock
                    
                    if tipo_ajuste == 'sumar':
                        nuevo_stock = stock_anterior + cantidad
                        movement_type = 'entrada'
                    elif tipo_ajuste == 'restar':
                        nuevo_stock = max(0, stock_anterior - cantidad)
                        movement_type = 'salida'
                    elif tipo_ajuste == 'establecer':
                        nuevo_stock = cantidad
                        movement_type = 'ajuste'
                    
                    # Solo actualizar si hay cambio
                    if nuevo_stock != stock_anterior:
                        producto.stock = nuevo_stock
                        producto.save()
                        
                        # Registrar movimiento
                        StockMovement.register_movement(
                            product=producto,
                            movement_type=movement_type,
                            reason=motivo,
                            quantity=abs(nuevo_stock - stock_anterior),
                            user=request.user,
                            notes=f"Ajuste masivo: {notas}" if notas else "Ajuste masivo de stock"
                        )
                    
                    productos_actualizados += 1
                
                messages.success(request, 
                    f'Se actualizó el stock de {productos_actualizados} productos correctamente. '
                    f'Motivo: {motivo}')
                
        except Exception as e:
            messages.error(request, f'Error al actualizar stock: {str(e)}')
    
    return redirect('dashboard-bodeguero')


@login_required
def reporte_inventario(request):
    """Generar reporte de inventario en Excel"""
    
    # Verificar permisos
    if not (request.user.is_staff or request.user.rol == 'bodeguero'):
        messages.error(request, 'No tienes permisos para generar reportes.')
        return redirect('dashboard-bodeguero')
    
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    # Crear respuesta HTTP para archivo CSV
    response = HttpResponse(content_type='text/csv')
    filename = f'inventario_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Crear writer CSV
    writer = csv.writer(response)
    
    # Headers
    writer.writerow([
        'ID', 'Nombre', 'Descripción', 'Marca', 'Categorías', 
        'Precio', 'Stock', 'Estado Stock', 'Valor Total',
        'Fecha Creación', 'Última Actualización'
    ])
    
    # Datos de productos
    productos = Product.objects.all().select_related('brand').prefetch_related('categories')
    
    for producto in productos:
        categorias = ', '.join([cat.name for cat in producto.categories.all()])
        valor_total = producto.price * producto.stock
        
        writer.writerow([
            producto.id,
            producto.name,
            producto.description[:100],  # Limitar descripción
            producto.brand.name if producto.brand else 'Sin marca',
            categorias or 'Sin categoría',
            producto.price,
            producto.stock,
            producto.stock_status,
            valor_total,
            producto.created_at.strftime('%Y-%m-%d %H:%M:%S') if producto.created_at else 'N/A',
            producto.updated_at.strftime('%Y-%m-%d %H:%M:%S') if producto.updated_at else 'N/A'
        ])
    
    return response

@login_required
def historial_stock(request):
    """Vista para ver el historial de movimientos de stock"""
    
    # Verificar permisos
    if not (request.user.is_staff or request.user.rol == 'bodeguero'):
        messages.error(request, 'No tienes permisos para ver el historial de stock.')
        return redirect('dashboard-bodeguero')
    
    # Filtros
    product_filter = request.GET.get('product', '')
    movement_type_filter = request.GET.get('movement_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Obtener movimientos
    movements = StockMovement.objects.select_related('product', 'user', 'order')
    
    # Aplicar filtros
    if product_filter:
        movements = movements.filter(product__id=product_filter)
    
    if movement_type_filter:
        movements = movements.filter(movement_type=movement_type_filter)
    
    if date_from:
        from datetime import datetime
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
        movements = movements.filter(created_at__date__gte=date_from_obj)
    
    if date_to:
        from datetime import datetime
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
        movements = movements.filter(created_at__date__lte=date_to_obj)
    
    # Paginación
    paginator = Paginator(movements, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Datos para filtros
    productos = Product.objects.all().order_by('name')
    movement_types = StockMovement.MOVEMENT_TYPE_CHOICES
    
    context = {
        'page_obj': page_obj,
        'productos': productos,
        'movement_types': movement_types,
        'product_filter': product_filter,
        'movement_type_filter': movement_type_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'dashboard-panel/bodega/historial-stock.html', context)

@role_required('contador')
def marcar_orden_entregada(request, order_id):
    """Vista para que el contador marque una orden como entregada y simule envío de correo"""
    
    order = get_object_or_404(Order, id=order_id)
    
    # Verificar que la orden pueda ser marcada como entregada
    if order.order_status == 'delivered':
        messages.warning(request, 'Esta orden ya ha sido marcada como entregada.')
        return redirect('order-detail-admin', order_id=order_id)
    
    if request.method == 'POST':
        # Marcar como entregada
        order.order_status = 'delivered'
        order.save()
        
        # Crear un contexto de datos simulados para el "correo"
        email_data = {
            'order_number': order.order_number,
            'customer_name': order.user.get_full_name() or order.user.username,
            'customer_email': order.user.email,
            'total_amount': order.total_amount,
            'delivery_date': timezone.now().strftime('%d/%m/%Y %H:%M'),
            'items_count': order.items.count(),
        }
        
        messages.success(
            request, 
            f'✅ Orden #{order.order_number} marcada como entregada exitosamente. '
            f'📧 Correo de confirmación enviado a {order.user.email}.'
        )
        
        # Agregar mensaje adicional con detalles de la "notificación"
        messages.info(
            request,
            f'📬 Notificación enviada: "Su orden #{order.order_number} ha sido entregada el '
            f'{email_data["delivery_date"]}. ¡Gracias por su compra!"'
        )
        
        return redirect('order-detail-admin', order_id=order_id)
    
    return redirect('order-detail-admin', order_id=order_id)

