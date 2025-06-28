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

class ContactMessage(models.Model):
    REASON_CHOICES = (
        ('ventas', 'Consulta de productos'),
        ('soporte', 'Soporte técnico'),
        ('reclamo', 'Reclamo'),
        ('otro', 'Otro'),
    )
    
    STATUS_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    )
    
    name = models.CharField(max_length=100, verbose_name="Nombre completo")
    email = models.EmailField(verbose_name="Correo electrónico")
    phone = models.CharField(max_length=15, verbose_name="Teléfono")
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, verbose_name="Motivo")
    message = models.TextField(verbose_name="Mensaje")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente', verbose_name="Estado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    attended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Atendido por"
    )
    response = models.TextField(blank=True, null=True, verbose_name="Respuesta")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
    
    def __str__(self):
        return f"{self.name} - {self.get_reason_display()} ({self.created_at.strftime('%d/%m/%Y')})"
    
    def get_status_color(self):
        colors = {
            'pendiente': 'warning',
            'en_proceso': 'info',
            'resuelto': 'success',
            'cerrado': 'secondary',
        }
        return colors.get(self.status, 'secondary')

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'En Proceso'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Información de envío
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=15)
    
    # Información de PayPal
    paypal_transaction_id = models.CharField(max_length=250, blank=True, null=True)
    paypal_payer_id = models.CharField(max_length=250, blank=True, null=True)
    paypal_payment_status = models.CharField(max_length=250, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
    
    def __str__(self):
        return f"Orden #{self.order_number} - {self.user.username}"
    
    def get_status_color(self):
        colors = {
            'pending': 'warning',
            'processing': 'info',
            'shipped': 'primary',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        return colors.get(self.order_status, 'secondary')
    
    def get_payment_status_color(self):
        colors = {
            'pending': 'warning',
            'completed': 'success',
            'failed': 'danger',
            'refunded': 'info',
        }
        return colors.get(self.payment_status, 'secondary')

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Precio al momento de la compra
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} - Orden #{self.order.order_number}"
    
    def total_price(self):
        return self.quantity * self.price