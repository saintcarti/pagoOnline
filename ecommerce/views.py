from django.shortcuts import render, redirect, get_object_or_404
from miPaypal.models import Product
from miPaypal.forms import ProductForm
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    product = Product.objects.all()

    return render(request,'ecommerce/index.html',{"products":product})


def login(request):
    return render(request,'auth/login.html')

def register(request):
    return render(request,'auth/register.html')


def products(request):
    product = Product.objects.all()

    return render(request,'ecommerce/products.html',{"products":product})

def about(request):
    return render(request,'ecommerce/about.html')

def contact(request):
    return render(request,'ecommerce/contact.html')


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