from django.urls import path
from .views import index,login,register,products


urlpatterns = [
    path('',index,name='index-page'),
    path('login/',login,name='login-page'),
    path('register/',register,name='register-page'),
    path('products/',products,name='products-page')
]