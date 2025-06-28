from django.contrib import admin
from .models import Product,TransaccionPaypal,CustomUser,Cart,CartItem,Brand,Category,ContactMessage,Order,OrderItem

# Register your models here.
admin.site.register(Product)
admin.site.register(TransaccionPaypal)
admin.site.register(CustomUser)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(ContactMessage)

# Configuración para OrderItem inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'total_price')

# Configuración para Order admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'order_status', 'payment_status', 'created_at')
    list_filter = ('order_status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    readonly_fields = ('order_number', 'total_amount', 'created_at', 'updated_at', 'paypal_transaction_id')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('order_number', 'user', 'total_amount', 'created_at', 'updated_at')
        }),
        ('Estado', {
            'fields': ('order_status', 'payment_status')
        }),
        ('Información de Envío', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_phone')
        }),
        ('Información de PayPal', {
            'fields': ('paypal_transaction_id', 'paypal_payer_id', 'paypal_payment_status')
        }),
    )