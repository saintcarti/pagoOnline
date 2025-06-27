from django.shortcuts import render
from miPaypal.models import Product


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
