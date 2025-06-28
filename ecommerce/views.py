from django.shortcuts import render, redirect, get_object_or_404
from miPaypal.models import Product, CustomUser
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

def contact(request):
    return render(request,'ecommerce/contact.html')

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
    products = Product.objects.all()
    return render(request, 'dashboard-panel/crud-products/list-product.html', {
        "products": products
    })


@admin_required
def crear_pview(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        product = Product(name=name, price=price, description=description, image=image)
        product.save()

        return redirect('list-products')

    return render(request, 'dashboard-panel/crud-products/create-product.html')

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