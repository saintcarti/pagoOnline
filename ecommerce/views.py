from django.shortcuts import render, redirect, get_object_or_404
from miPaypal.models import Product, CustomUser, Brand, Category
from miPaypal.forms import ProductForm, CustomUserCreationForm, StaffRegistrationForm,UserEditForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from miPaypal.decorators import admin_required
from django.core.paginator import Paginator
from django.db.models import Q 

# Create your views here.
def index(request):
    product = Product.objects.all()

    return render(request,'ecommerce/index.html',{"products":product})

def custom_logout(request):
    logout(request)
    return redirect('index-page')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('index-page')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
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
    product = Product.objects.all()

    return render(request,'ecommerce/products.html',{"products":product})

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
            # Aquí iría la lógica para procesar el formulario (enviar email, guardar en BD, etc.)
            
            # Redirigir para evitar reenvío del formulario al refrescar
            messages.success(request, '¡Gracias por tu mensaje! Nos pondremos en contacto contigo pronto.')
            return redirect('contact_success')
    
    return render(request, 'ecommerce/contact.html', context)

def contact_success(request):
    return render(request, 'ecommerce/contact.html', {'form_submitted': True})

@admin_required
def admin_settings(request):
    return render(request,'dashboard-panel/profile/admin-settings.html')

@admin_required
def admin_profile(request):
    return render(request,'dashboard-panel/profile/admin-profile.html')

@admin_required
def dashboard(request):
    return render(request,'dashboard-panel/dashboard.html')

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
    
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Aplicar filtros
    if role_filter:
        users = users.filter(rol=role_filter)
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(rut__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(users, 10)
    page_obj = paginator.get_page(page_number)
    
    # Pasar los roles definidos en el modelo al template
    return render(request, 'dashboard-panel/crud-users/list-user.html', {
        'page_obj': page_obj,
        'current_role': role_filter,
        'search_query': search_query or '',
        'user_roles': CustomUser.ROLES  # Esto es lo que necesitas añadir
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