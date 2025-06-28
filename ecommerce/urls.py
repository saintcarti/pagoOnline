from django.urls import path
from .views import *


urlpatterns = [
    ##ecommerce urls
    path('',index,name='index-page'),
    path('products/',products,name='products-page'),
    path('about/',about,name='about-page'),
    path('contact/',contact,name='contact-page'),
    ##Auth urls
    path('login/',login,name='login-page'),
    path('register/',register,name='register-page'),
    ##Panel administracion urls
    path('dashboard-panel/',dashboard,name='dashboard-panel-page'),
    path('admin-settings/',admin_settings,name='admin-settings-page'),
    path('admin-profile/',admin_profile,name='admin-profile-page'),
    ##CRUD Products
    path('list-products/', list_products, name='list-products'),
    path('create-product/', crear_pview, name='create-product'),
    path('update-product/<int:pk>/', update_product, name='update-product'),
    path('logout/', custom_logout, name='logout-fun'),
]