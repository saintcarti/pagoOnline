from django.urls import path
from .views import index,login,register,products,about,contact,dashboard
from .views import crear_pview, index,login,register,products,list_products,update_product


urlpatterns = [
    path('index/',index,name='index-page'),
    path('login/',login,name='login-page'),
    path('register/',register,name='register-page'),
    path('products/',products,name='products-page'),
    path('about/',about,name='about-page'),
    path('contact/',contact,name='contact-page'),
    path('dashboard-panel/',dashboard,name='dashboard-panel-page'),
    path('list-products/', list_products, name='list-products'),
    path('create-product/', crear_pview, name='create-product'),
    path('update-product/<int:pk>/', update_product, name='update-product'),
]