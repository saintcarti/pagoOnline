from django.contrib import admin
from .models import Product,TransaccionPaypal,CustomUser,Cart,CartItem

# Register your models here.
admin.site.register(Product)
admin.site.register(TransaccionPaypal)
admin.site.register(CustomUser)
admin.site.register(Cart)
admin.site.register(CartItem)