from django.contrib import admin
from .models import Product,TransaccionPaypal,CustomUser,Cart,CartItem,Brand,Category

# Register your models here.
admin.site.register(Product)
admin.site.register(TransaccionPaypal)
admin.site.register(CustomUser)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Brand)
admin.site.register(Category)