from django.urls import path
from .views import index,login,register,products,list_products


urlpatterns = [
    path('',index,name='index-page'),
    path('login/',login,name='login-page'),
    path('register/',register,name='register-page'),
    path('products/',products,name='products-page'),
    path('list-products/', list_products, name='list-products'),
]