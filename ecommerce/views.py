from django.shortcuts import render, redirect
from miPaypal.models import Product
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

@login_required
def list_products(request):
    products = Product.objects.all()
    return render(request, 'dashboard-panel/crud-products/list-product.html', {
        "products": products
    })