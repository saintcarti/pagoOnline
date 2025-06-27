from django.contrib import admin
from .models import Product,TransaccionPaypal

# Register your models here.
admin.site.register(Product)
admin.site.register(TransaccionPaypal)
