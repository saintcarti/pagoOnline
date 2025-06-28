from django.shortcuts import render, redirect, get_object_or_404
from miPaypal.models import Product, CustomUser, Brand, Category, ContactMessage, Order, OrderItem
from miPaypal.forms import ProductForm, CustomUserCreationForm, StaffRegistrationForm,UserEditForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from miPaypal.decorators import admin_required
from django.core.paginator import Paginator
from django.db.models import Q 
from django.contrib.admin.views.decorators import staff_member_required

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

@admin_required
def list_orders(request):
    """Vista para que los administradores vean todas las órdenes"""
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

@admin_required
def order_detail_admin(request, order_id):
    """Vista para que los administradores vean detalles de una orden"""
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

