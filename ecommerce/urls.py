from django.urls import path
from .views import index,login,register,products,about,contact,dashboard


urlpatterns = [
    path('',index,name='index-page'),
    path('login/',login,name='login-page'),
    path('register/',register,name='register-page'),
    path('products/',products,name='products-page'),
    path('about/',about,name='about-page'),
    path('contact/',contact,name='contact-page'),
    path('dashboard-panel/',dashboard,name='dashboard-panel-page')
]