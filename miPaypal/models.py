from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Product(models.Model):
    name=models.CharField(max_length=250)
    description= models.TextField()
    price= models.IntegerField()
    image = models.URLField(blank=True,null=True)

    def __str__(self)->str:
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity



class TransaccionPaypal(models.Model):
    payer_id=models.CharField(max_length=250)
    payment_date=models.DateTimeField()
    payment_status=models.CharField(max_length=250)
    quantity = models.IntegerField()
    invoice= models.CharField(max_length=250)
    first_name=models.CharField(max_length=250)
    payer_status=models.CharField(max_length=250)
    payer_email = models.CharField(max_length=250)
    txn_id=models.CharField(max_length=250)
    receiver_id=models.CharField(max_length=250)
    payment_gross = models.FloatField()
    custom=models.CharField(max_length=250)

    def __str__(self):
        return self.custom