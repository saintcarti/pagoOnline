from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Modelo de usuario personalizado DEBE estar primero
class CustomUser(AbstractUser):
    ROLES = (
        ('cliente', 'Cliente'),
        ('bodeguero', 'Bodeguero'),
        ('contador', 'Contador'),
        ('vendedor', 'Vendedor'),
    )
    
    rut = models.CharField(max_length=12, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    rol = models.CharField(max_length=10, choices=ROLES, default='cliente')
    
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    price = models.IntegerField()
    image = models.URLField(blank=True, null=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    categories = models.ManyToManyField('Category', related_name='products', blank=True)

    def __str__(self) -> str:
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

class TransaccionPaypal(models.Model):
    payer_id = models.CharField(max_length=250)
    payment_date = models.DateTimeField()
    payment_status = models.CharField(max_length=250)
    quantity = models.IntegerField()
    invoice = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    payer_status = models.CharField(max_length=250)
    payer_email = models.CharField(max_length=250)
    txn_id = models.CharField(max_length=250)
    receiver_id = models.CharField(max_length=250)
    payment_gross = models.FloatField()
    custom = models.CharField(max_length=250)

    def __str__(self):
        return self.custom