# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-successful/', views.payment_successful, name='payment-success'),
    path('payment-failed/', views.payment_failed, name='payment-failed'),
    path('paypal-ipn/', views.handle_paypal_ipn, name='paypal-ipn'),
]