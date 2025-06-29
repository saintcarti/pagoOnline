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
    ciudad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad")
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
    stock = models.PositiveIntegerField(default=0, help_text="Cantidad disponible en bodega")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
    
    @property
    def is_available(self):
        """Retorna True si el producto tiene stock disponible"""
        return self.stock > 0
    
    @property
    def stock_status(self):
        """Retorna el estado del stock para mostrar en las vistas"""
        if self.stock == 0:
            return "Sin stock"
        elif self.stock <= 5:
            return "Stock bajo"
        elif self.stock <= 20:
            return "Stock medio"
        else:
            return "Stock alto"

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
        ('confirmed', 'Confirmada'),
        ('processing', 'En Proceso'),
        ('packed', 'Empacada'),
        ('shipped', 'Enviada'),
        ('delivered', 'Entregada'),
        ('cancelled', 'Cancelada'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
    ]
    
    ORDER_TYPE_CHOICES = [
        ('online', 'Compra Online'),
        ('manual', 'Orden Manual'),
        ('phone', 'Orden Telefónica'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Tipo de orden y vendedor
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='online')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_orders',
        verbose_name="Creada por"
    )
    
    # Información de envío
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=15)
    
    # Notas y seguimiento
    notes = models.TextField(blank=True, null=True, verbose_name="Notas adicionales")
    tracking_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de seguimiento")
    estimated_delivery = models.DateTimeField(blank=True, null=True, verbose_name="Entrega estimada")
    
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
            'confirmed': 'info',
            'processing': 'primary',
            'packed': 'secondary',
            'shipped': 'success',
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
    
    def can_be_cancelled(self):
        """Determina si la orden puede ser cancelada"""
        return self.order_status in ['pending', 'confirmed']
    
    def can_be_shipped(self):
        """Determina si la orden puede ser enviada"""
        return self.order_status in ['confirmed', 'processing', 'packed']
    
    def get_next_status(self):
        """Obtiene el siguiente estado posible"""
        status_flow = {
            'pending': 'confirmed',
            'confirmed': 'processing',
            'processing': 'packed',
            'packed': 'shipped',
            'shipped': 'delivered',
        }
        return status_flow.get(self.order_status)
    
    def get_status_progress_percentage(self):
        """Obtiene el porcentaje de progreso del estado"""
        progress = {
            'pending': 10,
            'confirmed': 25,
            'processing': 50,
            'packed': 75,
            'shipped': 90,
            'delivered': 100,
            'cancelled': 0,
        }
        return progress.get(self.order_status, 0)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Precio al momento de la compra
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} - Orden #{self.order.order_number}"
    
    def total_price(self):
        return self.quantity * self.price

class StockMovement(models.Model):
    """Modelo para registrar todos los movimientos de stock para auditoría"""
    
    MOVEMENT_TYPE_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('devolucion', 'Devolución'),
        ('dano', 'Producto Dañado'),
        ('vencimiento', 'Vencimiento'),
    ]
    
    REASON_CHOICES = [
        ('compra', 'Compra a proveedor'),
        ('venta', 'Venta a cliente'),
        ('reabastecimiento', 'Reabastecimiento'),
        ('inventario', 'Ajuste por inventario'),
        ('dano', 'Productos dañados'),
        ('vencimiento', 'Productos vencidos'),
        ('devolucion_cliente', 'Devolución de cliente'),
        ('devolucion_proveedor', 'Devolución a proveedor'),
        ('transferencia', 'Transferencia entre bodegas'),
        ('perdida', 'Pérdida o robo'),
        ('otro', 'Otro motivo'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    quantity = models.IntegerField()  # Positivo para entradas, negativo para salidas
    stock_before = models.PositiveIntegerField()  # Stock antes del movimiento
    stock_after = models.PositiveIntegerField()   # Stock después del movimiento
    
    # Usuario que realizó el movimiento
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='stock_movements'
    )
    
    # Referencia a orden si el movimiento fue por una venta
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Información adicional
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")
    reference_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de referencia")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
    
    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} ({self.quantity}) - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def get_movement_icon(self):
        """Retorna el ícono apropiado para el tipo de movimiento"""
        icons = {
            'entrada': 'fas fa-arrow-up text-success',
            'salida': 'fas fa-arrow-down text-danger',
            'ajuste': 'fas fa-edit text-warning',
            'devolucion': 'fas fa-undo text-info',
            'dano': 'fas fa-exclamation-triangle text-danger',
            'vencimiento': 'fas fa-clock text-warning',
        }
        return icons.get(self.movement_type, 'fas fa-exchange-alt')
    
    def get_quantity_display(self):
        """Muestra la cantidad con signo apropiado"""
        if self.movement_type in ['entrada', 'devolucion']:
            return f"+{self.quantity}"
        else:
            return f"-{abs(self.quantity)}"
    
    @classmethod
    def register_movement(cls, product, movement_type, reason, quantity, user, order=None, notes=None, reference_number=None):
        """Método para registrar un movimiento de stock de forma segura"""
        
        stock_before = product.stock
        
        if movement_type in ['entrada', 'devolucion']:
            new_stock = stock_before + quantity
        else:  # salida, ajuste, daño, vencimiento
            new_stock = max(0, stock_before - quantity)
        
        # Actualizar stock del producto
        product.stock = new_stock
        product.save()
        
        # Crear registro del movimiento
        movement = cls.objects.create(
            product=product,
            movement_type=movement_type,
            reason=reason,
            quantity=quantity if movement_type in ['entrada', 'devolucion'] else -quantity,
            stock_before=stock_before,
            stock_after=new_stock,
            user=user,
            order=order,
            notes=notes,
            reference_number=reference_number
        )
        
        return movement