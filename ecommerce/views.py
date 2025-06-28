from django.shortcuts import render, redirect, get_object_or_404
from miPaypal.models import Product
from miPaypal.forms import ProductForm, CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from miPaypal.decorators import admin_required, role_required

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
    
    return render(request, 'contact.html', context)

def contact_success(request):
    return render(request, 'contact.html', {'form_submitted': True})

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
        image = request.POST.get('image')

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