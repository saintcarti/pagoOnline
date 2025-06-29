from django.shortcuts import render, redirect, get_object_or_404
from miPaypal.models import Product, CustomUser, Brand, Category, ContactMessage, Order, OrderItem, StockMovement
from miPaypal.forms import ProductForm, CustomUserCreationForm, StaffRegistrationForm, UserEditForm, ManualOrderForm, OrderStatusUpdateForm, OrderItemForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from miPaypal.decorators import admin_required, admin_only_required, role_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, F, Avg
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, timedelta
import calendar
import io
import base64

# Importaciones para PDF
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.validators import Auto

# Importaciones para gráficos
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
            
            # Redirigir según el rol del usuario
            if user.is_staff:
                if user.rol == 'contador':
                    return redirect('dashboard-contador')
                elif user.rol == 'bodeguero':
                    return redirect('dashboard-bodeguero')
                else:
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

@admin_only_required
@admin_only_required
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

@admin_only_required
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

@admin_only_required
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

@admin_only_required
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


@admin_only_required
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

@admin_only_required
def delete_product(request, pk):
    """Vista para eliminar productos"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f'Producto {product.name} eliminado correctamente')
        return redirect('list-products')
    return render(request, 'dashboard-panel/crud-products/confirm-delete.html', {'product': product})


@role_required('bodeguero', 'vendedor')
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

@admin_only_required
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

@admin_only_required
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

@admin_only_required
def delete_user(request, user_id):
    """Vista para eliminar usuarios"""
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuario {username} eliminado correctamente')
        return redirect('list-user')  # Cambiado a 'list-user' para consistencia
    return render(request, 'dashboard-panel/crud-users/confirm-delete.html', {'user': user})

@admin_only_required
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

@admin_only_required
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

@admin_only_required
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

@admin_only_required
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

@admin_only_required
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

@admin_only_required
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


@role_required('bodeguero', 'vendedor')
def vista_bodega(request):
    """Vista de bodega para vendedores y bodegueros - muestra productos con información de stock"""
    
    # Verificar que el usuario sea vendedor o bodeguero (NO contador)
    if not (request.user.is_staff and request.user.rol in ['vendedor', 'bodeguero']) and not (request.user.rol in ['vendedor', 'bodeguero']):
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


# Vistas para gestión de órdenes por vendedores

@login_required
def lista_ordenes_vendedor(request):
    """Vista para que vendedores y bodegueros vean las órdenes"""
    
    # Verificar permisos - ahora incluye bodegueros
    if not (request.user.is_staff or request.user.rol in ['vendedor', 'bodeguero']):
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
    """Vista de detalle de orden para vendedores y bodegueros"""
    
    # Verificar permisos - ahora incluye bodegueros
    if not (request.user.is_staff or request.user.rol in ['vendedor', 'bodeguero']):
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

@login_required
def aprobar_pedido_vendedor(request, order_id):
    """Vista para que vendedores y bodegueros puedan aprobar pedidos"""
    
    # Verificar que el usuario sea vendedor, bodeguero o staff
    if not (request.user.is_staff or request.user.rol in ['vendedor', 'bodeguero']):
        messages.error(request, 'No tienes permisos para aprobar pedidos.')
        return redirect('index-page')
    
    order = get_object_or_404(Order, id=order_id)
    
    # Solo se pueden aprobar órdenes pendientes
    if order.order_status != 'pending':
        messages.warning(request, 'Esta orden ya ha sido procesada.')
        return redirect('lista-ordenes-vendedor')
    
    if request.method == 'POST':
        # Aprobar el pedido
        order.order_status = 'confirmed'
        order.approved_by = request.user
        order.approved_at = timezone.now()
        order.save()
        
        # Registrar movimiento de stock
        for item in order.items.all():
            if hasattr(item.product, 'stock'):
                # Reducir stock del producto
                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity
                    item.product.save()
                    
                    # Registrar movimiento de stock
                    StockMovement.register_movement(
                        product=item.product,
                        movement_type='salida',
                        reason='venta',
                        quantity=item.quantity,
                        user=request.user,
                        order=order,
                        notes=f'Venta aprobada - Orden #{order.order_number}'
                    )
                else:
                    messages.warning(request, f'Stock insuficiente para {item.product.name}. Stock actual: {item.product.stock}')
        
        messages.success(request, f'Pedido #{order.order_number} aprobado exitosamente.')
        return redirect('detalle-orden-vendedor', order_id=order.id)
    
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    
    return render(request, 'dashboard-panel/ordenes-vendedor/aprobar-pedido.html', context)

@login_required
def rechazar_pedido_vendedor(request, order_id):
    """Vista para que vendedores y bodegueros puedan rechazar pedidos"""
    
    # Verificar que el usuario sea vendedor, bodeguero o staff
    if not (request.user.is_staff or request.user.rol in ['vendedor', 'bodeguero']):
        messages.error(request, 'No tienes permisos para rechazar pedidos.')
        return redirect('index-page')
    
    order = get_object_or_404(Order, id=order_id)
    
    # Solo se pueden rechazar órdenes pendientes
    if order.order_status != 'pending':
        messages.warning(request, 'Esta orden ya ha sido procesada.')
        return redirect('lista-ordenes-vendedor')
    
    if request.method == 'POST':
        motivo_rechazo = request.POST.get('motivo_rechazo', '').strip()
        
        if not motivo_rechazo:
            messages.error(request, 'Debe proporcionar un motivo de rechazo.')
            return redirect('aprobar-pedido-vendedor', order_id=order_id)
        
        # Rechazar el pedido
        order.order_status = 'cancelled'
        order.notes = f"RECHAZADO: {motivo_rechazo}"
        order.save()
        
        messages.success(request, f'Pedido #{order.order_number} rechazado.')
        return redirect('lista-ordenes-vendedor')
    
    return redirect('aprobar-pedido-vendedor', order_id=order_id)

# Vistas específicas para bodegueros

@login_required
def dashboard_bodeguero(request):
    """Dashboard principal para bodegueros"""
    
    # Verificar que el usuario sea bodeguero únicamente
    if not (request.user.rol == 'bodeguero'):
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

@role_required('contador')
def dashboard_contador(request):
    """Dashboard principal para contadores"""
    
    # Obtener estadísticas de órdenes
    from datetime import datetime, timedelta
    hoy = datetime.now().date()
    
    # Estadísticas generales
    total_ordenes = Order.objects.count()
    ordenes_pendientes = Order.objects.filter(order_status__in=['pending', 'confirmed', 'processing']).count()
    ordenes_enviadas = Order.objects.filter(order_status='shipped').count()
    ordenes_entregadas_hoy = Order.objects.filter(
        order_status='delivered',
        updated_at__date=hoy
    ).count()
    
    # Órdenes que necesitan atención del contador
    ordenes_para_entrega = Order.objects.filter(
        order_status='shipped'
    ).order_by('-updated_at')[:10]
    
    # Órdenes recientes
    ordenes_recientes = Order.objects.all().order_by('-created_at')[:5]
    
    # Estadísticas por estado
    ordenes_por_estado = {}
    for choice in Order.ORDER_STATUS_CHOICES:
        estado = choice[0]
        count = Order.objects.filter(order_status=estado).count()
        ordenes_por_estado[choice[1]] = count
    
    # Estadísticas de pagos
    pagos_completados = Order.objects.filter(payment_status='completed').count()
    pagos_pendientes = Order.objects.filter(payment_status='pending').count()
    
    # Resumen de ventas del mes
    inicio_mes = hoy.replace(day=1)
    ordenes_mes = Order.objects.filter(
        created_at__date__gte=inicio_mes,
        payment_status='completed'
    )
    ventas_mes = sum(orden.total_amount for orden in ordenes_mes)
    
    stats = {
        'total_ordenes': total_ordenes,
        'ordenes_pendientes': ordenes_pendientes,
        'ordenes_enviadas': ordenes_enviadas,
        'ordenes_entregadas_hoy': ordenes_entregadas_hoy,
        'pagos_completados': pagos_completados,
        'pagos_pendientes': pagos_pendientes,
        'ventas_mes': ventas_mes,
        'ordenes_mes_count': ordenes_mes.count(),
    }
    
    context = {
        'stats': stats,
        'ordenes_para_entrega': ordenes_para_entrega,
        'ordenes_recientes': ordenes_recientes,
        'ordenes_por_estado': ordenes_por_estado,
    }
    
    return render(request, 'dashboard-panel/contador/dashboard-contador.html', context)

# Vistas para generación de informes mensuales

@admin_only_required
def informes_mensuales(request):
    """Vista para mostrar el panel de informes mensuales"""
    # Obtener año y mes actual
    hoy = datetime.now()
    año_actual = hoy.year
    mes_actual = hoy.month
    
    # Obtener parámetros de filtro
    año_seleccionado = request.GET.get('año', año_actual)
    mes_seleccionado = request.GET.get('mes', mes_actual)
    
    try:
        año_seleccionado = int(año_seleccionado)
        mes_seleccionado = int(mes_seleccionado)
    except (ValueError, TypeError):
        año_seleccionado = año_actual
        mes_seleccionado = mes_actual
    
    # Calcular fechas del mes seleccionado
    primer_dia_mes = datetime(año_seleccionado, mes_seleccionado, 1)
    ultimo_dia_mes = datetime(año_seleccionado, mes_seleccionado, 
                             calendar.monthrange(año_seleccionado, mes_seleccionado)[1])
    
    # Obtener estadísticas del mes
    ordenes_mes = Order.objects.filter(
        created_at__date__gte=primer_dia_mes.date(),
        created_at__date__lte=ultimo_dia_mes.date()
    )
    
    # Estadísticas básicas
    total_ordenes = ordenes_mes.count()
    ordenes_completadas = ordenes_mes.filter(payment_status='completed').count()
    ventas_totales = ordenes_mes.filter(payment_status='completed').aggregate(
        total=Sum('total_amount'))['total'] or 0
    
    # Promedio por orden
    promedio_orden = ventas_totales / ordenes_completadas if ordenes_completadas > 0 else 0
    
    # Productos más vendidos del mes
    productos_top = OrderItem.objects.filter(
        order__created_at__date__gte=primer_dia_mes.date(),
        order__created_at__date__lte=ultimo_dia_mes.date(),
        order__payment_status='completed'
    ).values(
        'product__name', 'product__price'
    ).annotate(
        cantidad_vendida=Sum('quantity'),
        ingresos=Sum(F('quantity') * F('price'))
    ).order_by('-cantidad_vendida')[:10]
    
    # Ventas por día del mes
    ventas_diarias = []
    for dia in range(1, calendar.monthrange(año_seleccionado, mes_seleccionado)[1] + 1):
        fecha_dia = datetime(año_seleccionado, mes_seleccionado, dia).date()
        ventas_dia = ordenes_mes.filter(
            created_at__date=fecha_dia,
            payment_status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        ventas_diarias.append({
            'dia': dia,
            'fecha': fecha_dia,
            'ventas': ventas_dia
        })
    
    # Generar lista de años disponibles (últimos 5 años)
    años_disponibles = list(range(año_actual - 4, año_actual + 1))
    meses_disponibles = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]
    
    context = {
        'año_seleccionado': año_seleccionado,
        'mes_seleccionado': mes_seleccionado,
        'mes_nombre': calendar.month_name[mes_seleccionado],
        'años_disponibles': años_disponibles,
        'meses_disponibles': meses_disponibles,
        'total_ordenes': total_ordenes,
        'ordenes_completadas': ordenes_completadas,
        'ventas_totales': ventas_totales,
        'promedio_orden': promedio_orden,
        'productos_top': productos_top,
        'ventas_diarias': ventas_diarias,
        'primer_dia_mes': primer_dia_mes,
        'ultimo_dia_mes': ultimo_dia_mes,
    }
    
    return render(request, 'dashboard-panel/informes/informes-mensuales.html', context)


@admin_only_required
def generar_informe_pdf(request):
    """Generar informe mensual en formato PDF"""
    # Obtener parámetros
    año = int(request.GET.get('año', datetime.now().year))
    mes = int(request.GET.get('mes', datetime.now().month))
    
    # Calcular fechas del mes
    primer_dia_mes = datetime(año, mes, 1)
    ultimo_dia_mes = datetime(año, mes, calendar.monthrange(año, mes)[1])
    
    # Crear respuesta HTTP para PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="informe_ventas_{calendar.month_name[mes]}_{año}.pdf"'
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Título del informe
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Centrado
        textColor=colors.darkblue
    )
    
    title = Paragraph(
        f"INFORME DE VENTAS - {calendar.month_name[mes].upper()} {año}",
        title_style
    )
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Información de la empresa
    company_style = ParagraphStyle(
        'CompanyInfo',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        textColor=colors.grey
    )
    
    company_info = Paragraph(
        "FERREMAS - Sistema de Gestión de Ventas<br/>Generado el: " + 
        datetime.now().strftime("%d/%m/%Y %H:%M"),
        company_style
    )
    story.append(company_info)
    story.append(Spacer(1, 30))
    
    # Obtener datos del mes
    ordenes_mes = Order.objects.filter(
        created_at__date__gte=primer_dia_mes.date(),
        created_at__date__lte=ultimo_dia_mes.date()
    )
    
    ordenes_completadas = ordenes_mes.filter(payment_status='completed')
    ventas_totales = ordenes_completadas.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Resumen ejecutivo
    resumen_data = [
        ['CONCEPTO', 'VALOR'],
        ['Total de Órdenes', f"{ordenes_mes.count():,}"],
        ['Órdenes Completadas', f"{ordenes_completadas.count():,}"],
        ['Ventas Totales', f"${ventas_totales:,.2f}"],
        ['Promedio por Orden', f"${(ventas_totales / ordenes_completadas.count() if ordenes_completadas.count() > 0 else 0):,.2f}"],
        ['Tasa de Conversión', f"{(ordenes_completadas.count() / ordenes_mes.count() * 100 if ordenes_mes.count() > 0 else 0):.1f}%"],
    ]
    
    resumen_table = Table(resumen_data, colWidths=[3*inch, 2*inch])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(Paragraph("RESUMEN EJECUTIVO", styles['Heading2']))
    story.append(Spacer(1, 12))
    story.append(resumen_table)
    story.append(Spacer(1, 30))
    
    # Productos más vendidos
    productos_top = OrderItem.objects.filter(
        order__created_at__date__gte=primer_dia_mes.date(),
        order__created_at__date__lte=ultimo_dia_mes.date(),
        order__payment_status='completed'
    ).values(
        'product__name', 'product__price'
    ).annotate(
        cantidad_vendida=Sum('quantity'),
        ingresos=Sum(F('quantity') * F('price'))
    ).order_by('-cantidad_vendida')[:10]
    
    if productos_top:
        productos_data = [['PRODUCTO', 'CANTIDAD', 'PRECIO UNIT.', 'INGRESOS']]
        for producto in productos_top:
            productos_data.append([
                producto['product__name'][:30] + ('...' if len(producto['product__name']) > 30 else ''),
                f"{producto['cantidad_vendida']:,}",
                f"${producto['product__price']:,.2f}",
                f"${producto['ingresos']:,.2f}"
            ])
        
        productos_table = Table(productos_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch])
        productos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(Paragraph("TOP 10 PRODUCTOS MÁS VENDIDOS", styles['Heading2']))
        story.append(Spacer(1, 12))
        story.append(productos_table)
        story.append(Spacer(1, 30))
    
    # Ventas por estado de orden
    estados_ordenes = ordenes_mes.values('order_status').annotate(
        cantidad=Count('id'),
        total_ventas=Sum('total_amount')
    ).order_by('-cantidad')
    
    if estados_ordenes:
        estados_data = [['ESTADO', 'CANTIDAD', 'VALOR TOTAL']]
        for estado in estados_ordenes:
            estado_nombre = dict(Order.ORDER_STATUS_CHOICES).get(estado['order_status'], estado['order_status'])
            estados_data.append([
                estado_nombre,
                f"{estado['cantidad']:,}",
                f"${estado['total_ventas'] or 0:,.2f}"
            ])
        
        estados_table = Table(estados_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        estados_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(Paragraph("VENTAS POR ESTADO DE ORDEN", styles['Heading2']))
        story.append(Spacer(1, 12))
        story.append(estados_table)
        story.append(Spacer(1, 30))
    
    # Nueva página para gráficos
    story.append(PageBreak())
    
    # Generar gráfico de ventas diarias
    try:
        grafico_ventas = generar_grafico_ventas_diarias(año, mes)
        if grafico_ventas:
            story.append(Paragraph("GRÁFICO DE VENTAS DIARIAS", styles['Heading2']))
            story.append(Spacer(1, 12))
            story.append(grafico_ventas)
            story.append(Spacer(1, 30))
    except Exception as e:
        print(f"Error generando gráfico: {e}")
    
    # Pie de página con información adicional
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,
        textColor=colors.grey
    )
    
    footer_text = f"""
    <br/><br/>
    Este informe fue generado automáticamente por el sistema Ferremas.<br/>
    Período: {primer_dia_mes.strftime('%d/%m/%Y')} - {ultimo_dia_mes.strftime('%d/%m/%Y')}<br/>
    Total de páginas: 2
    """
    
    story.append(Paragraph(footer_text, footer_style))
    
    # Construir el PDF
    doc.build(story)
    
    return response


def generar_grafico_ventas_diarias(año, mes):
    """Generar gráfico de ventas diarias para incluir en el PDF"""
    try:
        # Configurar matplotlib para usar backend no interactivo
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Obtener datos de ventas diarias
        primer_dia = datetime(año, mes, 1).date()
        ultimo_dia = datetime(año, mes, calendar.monthrange(año, mes)[1]).date()
        
        ventas_diarias = []
        fechas = []
        
        for dia in range(1, calendar.monthrange(año, mes)[1] + 1):
            fecha_dia = datetime(año, mes, dia).date()
            ventas_dia = Order.objects.filter(
                created_at__date=fecha_dia,
                payment_status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            ventas_diarias.append(float(ventas_dia))
            fechas.append(fecha_dia)
        
        # Crear el gráfico
        ax.plot(fechas, ventas_diarias, marker='o', linewidth=2, markersize=4)
        ax.set_title(f'Ventas Diarias - {calendar.month_name[mes]} {año}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Día del Mes')
        ax.set_ylabel('Ventas ($)')
        ax.grid(True, alpha=0.3)
        
        # Formatear eje Y para mostrar valores en miles
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Formatear eje X para mostrar solo algunos días
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Guardar en memoria
        buffer = io.BytesIO()
        plt.savefig(buffer, format='PNG', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        
        # Crear objeto Image para ReportLab
        img = Image(buffer, width=6*inch, height=3.6*inch)
        
        plt.close(fig)
        return img
        
    except Exception as e:
        print(f"Error creando gráfico: {e}")
        return None

# Vistas específicas para el contador - Historial de Transacciones

@role_required('contador')
def historial_transacciones_contador(request):
    """Vista para que el contador vea el historial completo de transacciones"""
    
    # Obtener parámetros de filtro
    status_filter = request.GET.get('status')
    payment_filter = request.GET.get('payment_status')
    search_query = request.GET.get('search')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    per_page = request.GET.get('per_page', '25')
    
    try:
        per_page = int(per_page)
        if per_page not in [10, 25, 50, 100]:
            per_page = 25
    except (ValueError, TypeError):
        per_page = 25
    
    # Base queryset con todas las órdenes
    orders_list = Order.objects.all().select_related('user').prefetch_related('items__product')
    
    # Aplicar filtros
    if status_filter:
        orders_list = orders_list.filter(order_status=status_filter)
    
    if payment_filter:
        orders_list = orders_list.filter(payment_status=payment_filter)
    
    if search_query:
        orders_list = orders_list.filter(
            Q(order_number__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            orders_list = orders_list.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            orders_list = orders_list.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Ordenar por fecha de creación (más recientes primero)
    orders_list = orders_list.order_by('-created_at')
    
    # Estadísticas rápidas
    total_ordenes = orders_list.count()
    ordenes_completadas = orders_list.filter(payment_status='completed').count()
    ventas_totales = orders_list.filter(payment_status='completed').aggregate(
        total=Sum('total_amount'))['total'] or 0
    ordenes_pendientes = orders_list.filter(order_status__in=['pending', 'confirmed']).count()
    
    # Configurar paginación
    paginator = Paginator(orders_list, per_page)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    # Estadísticas por período
    hoy = datetime.now().date()
    inicio_mes = hoy.replace(day=1)
    ordenes_mes = orders_list.filter(created_at__date__gte=inicio_mes)
    ventas_mes = ordenes_mes.filter(payment_status='completed').aggregate(
        total=Sum('total_amount'))['total'] or 0
    
    context = {
        'orders': orders,
        'status_choices': Order.ORDER_STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
        'current_status': status_filter,

        'current_payment_status': payment_filter,
        'search_query': search_query or '',
        'date_from': date_from or '',
        'date_to': date_to or '',
        'per_page': per_page,
        'stats': {
            'total_ordenes': total_ordenes,
            'ordenes_completadas': ordenes_completadas,
            'ventas_totales': ventas_totales,
            'ordenes_pendientes': ordenes_pendientes,
            'ordenes_mes': ordenes_mes.count(),
            'ventas_mes': ventas_mes,
        }
    }
    
    return render(request, 'dashboard-panel/contador/historial-transacciones.html', context)


@role_required('contador')
def detalle_transaccion_contador(request, order_id):
    """Vista detallada de una transacción específica para el contador"""
    order = get_object_or_404(Order, id=order_id)
    
    # Obtener items de la orden
    order_items = order.items.all().select_related('product')
    
    # Calcular información adicional
    total_items = sum(item.quantity for item in order_items)
    subtotal = sum(item.quantity * item.price for item in order_items)
    
    # Información del cliente
    customer = order.user
    
    context = {
        'order': order,
        'order_items': order_items,
        'customer': customer,
        'total_items': total_items,
        'subtotal': subtotal,
        'status_choices': Order.ORDER_STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
    }
    
    return render(request, 'dashboard-panel/contador/detalle-transaccion.html', context)


@role_required('contador')
def exportar_transacciones_contador(request):
    """Exportar historial de transacciones a CSV para el contador"""
    from django.http import HttpResponse
    import csv
    from datetime import datetime
    
    # Obtener los mismos filtros que en el historial
    status_filter = request.GET.get('status')
    payment_filter = request.GET.get('payment_status')
    search_query = request.GET.get('search')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Aplicar filtros
    orders_list = Order.objects.all().select_related('user')
    
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
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            orders_list = orders_list.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            orders_list = orders_list.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv')
    filename = f'historial_transacciones_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Crear writer CSV
    writer = csv.writer(response)
    
    # Headers
    writer.writerow([
        'Número de Orden',
        'Cliente',
        'Email Cliente',
        'Fecha de Creación',
        'Estado de Orden',
        'Estado de Pago',
        'Total',
        'Método de Pago',
        'Fecha de Actualización'
    ])
    
    # Datos de las órdenes
    for order in orders_list.order_by('-created_at'):
        writer.writerow([
            order.order_number,
            order.user.get_full_name() or order.user.username,
            order.user.email,
            order.created_at.strftime('%d/%m/%Y %H:%M'),
            dict(Order.ORDER_STATUS_CHOICES).get(order.order_status, order.order_status),
            dict(Order.PAYMENT_STATUS_CHOICES).get(order.payment_status, order.payment_status),
            f'${order.total_amount:.2f}',
            order.payment_method or 'No especificado',
            order.updated_at.strftime('%d/%m/%Y %H:%M')
        ])
    
    return response

@login_required
def view_cart(request):
    """Vista del carrito con descuento del 13% si hay más de 4 productos"""
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    total_items = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total += subtotal
            total_items += quantity
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            # Remover producto que ya no existe
            del cart[product_id]
            request.session['cart'] = cart
    
    # Aplicar descuento del 13% si hay más de 4 productos
    discount_percentage = 0
    discount_amount = 0
    final_total = total
    
    if total_items > 4:
        discount_percentage = 13
        discount_amount = total * 0.13
        final_total = total - discount_amount
    
    # Actualizar contador del carrito en la sesión
    request.session['cart_count'] = total_items
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'total_items': total_items,
        'discount_percentage': discount_percentage,
        'discount_amount': discount_amount,
        'final_total': final_total,
        'has_discount': total_items > 4,
    }
    
    return render(request, 'ecommerce/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    """Agregar producto al carrito"""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        
        # Verificar stock disponible
        try:
            product = Product.objects.get(id=product_id)
            current_cart_quantity = cart.get(str(product_id), 0)
            total_requested = current_cart_quantity + quantity
            
            if total_requested > product.stock:
                messages.error(request, f'Stock insuficiente. Solo hay {product.stock} unidades disponibles.')
                return redirect('products-page')
            
            # Agregar al carrito
            cart[str(product_id)] = total_requested
            request.session['cart'] = cart
            
            # Actualizar contador del carrito
            cart_count = sum(cart.values())
            request.session['cart_count'] = cart_count
            
            messages.success(request, f'{product.name} agregado al carrito.')
            
        except Product.DoesNotExist:
            messages.error(request, 'Producto no encontrado.')
    
    return redirect('products-page')


@login_required
def update_cart_item(request, product_id):
    """Actualizar cantidad de un producto en el carrito"""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        
        try:
            product = Product.objects.get(id=product_id)
            
            if quantity > product.stock:
                messages.error(request, f'Stock insuficiente. Solo hay {product.stock} unidades disponibles.')
            elif quantity > 0:
                cart[str(product_id)] = quantity
                messages.success(request, 'Carrito actualizado.')
            else:
                # Remover del carrito si cantidad es 0
                cart.pop(str(product_id), None)
                messages.success(request, f'{product.name} removido del carrito.')
            
            request.session['cart'] = cart
            
            # Actualizar contador del carrito
            cart_count = sum(cart.values())
            request.session['cart_count'] = cart_count
            
        except Product.DoesNotExist:
            messages.error(request, 'Producto no encontrado.')
    
    return redirect('view_cart')


@login_required
def remove_from_cart(request, product_id):
    """Remover producto del carrito"""
    cart = request.session.get('cart', {})
    
    if str(product_id) in cart:
        try:
            product = Product.objects.get(id=product_id)
            cart.pop(str(product_id))
            request.session['cart'] = cart
            
            # Actualizar contador del carrito
            cart_count = sum(cart.values())
            request.session['cart_count'] = cart_count
            
            messages.success(request, f'{product.name} removido del carrito.')
        except Product.DoesNotExist:
            cart.pop(str(product_id))
            request.session['cart'] = cart
    
    return redirect('view_cart')


@login_required
def clear_cart(request):
    """Limpiar todo el carrito"""
    request.session['cart'] = {}
    request.session['cart_count'] = 0
    messages.success(request, 'Carrito vaciado.')
    return redirect('view_cart')