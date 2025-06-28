from django.shortcuts import render, redirect, get_object_or_404
from miPaypal.models import Product
from miPaypal.forms import ProductForm, CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages

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

def logout(request):
    pass

def admin_settings(request):
    return render(request,'dashboard-panel/profile/admin-settings.html')

def admin_profile(request):
    return render(request,'dashboard-panel/profile/admin-profile.html')


def dashboard(request):
    return render(request,'dashboard-panel/dashboard.html')

@login_required
def list_products(request):
    products = Product.objects.all()
    return render(request, 'dashboard-panel/crud-products/list-product.html', {
        "products": products
    })


@login_required
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

@login_required
def list_products(request):
    products = Product.objects.all()
    return render(request, 'dashboard-panel/crud-products/list-product.html', {
        "products": products
    })

@login_required
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
def about(request):
    return render(request,'ecommerce/about.html')

def contact(request):
    return render(request,'ecommerce/contact.html')


def dashboard(request):
    return render(request,'dashboard-panel/dashboard.html')

def admin_required(view_func=None, redirect_url='index-page'):
    """
    Decorador que verifica si el usuario está autenticado y es staff/admin
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url=redirect_url
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator