from django.urls import path
from .views import *

urlpatterns = [
    # ecommerce urls
    path('', index, name='index-page'),
    path('products/', products, name='products-page'),
    path('about/', about, name='about-page'),
    path('contact/', contact_view, name='contact-page'),
    
    # Auth urls
    path('login/', login, name='login-page'),
    path('register/', register, name='register-page'),
    path('logout/', custom_logout, name='logout-fun'),
    
    # Panel administración
    path('dashboard-panel/', dashboard, name='dashboard-panel-page'),
    path('admin-settings/', admin_settings, name='admin-settings-page'),
    path('admin-profile/', admin_profile, name='admin-profile-page'),
    path('change-password/', change_password, name='change-password'),
    
    # Perfil de usuario regular
    path('profile/', user_profile, name='user-profile-page'),
    path('profile/change-password/', user_change_password, name='user-change-password'),
    
    # CRUD Products
    path('list-products/', list_products, name='list-products'),
    path('create-product/', crear_pview, name='create-product'),
    path('update-product/<int:pk>/', update_product, name='update-product'),
    path('delete-product/<int:pk>/', delete_product, name='delete-product'),
    path('product-detail/<int:pk>/', product_detail, name='product-detail'),
    
    # CRUD Users
    path('dashboard/users/', list_user, name='list-user'),
    path('dashboard/users/view/<int:user_id>/', view_user_detail, name='view-user-detail'),
    path('dashboard/users/delete/<int:user_id>/', delete_user, name='delete-user'),
    path('dashboard/users/edit/<int:user_id>/', edit_user, name='edit-user'),
    path('dashboard/users/create/', staff_register, name='create-user'),
    
    # CRUD Contact Messages
    path('dashboard/messages/', list_contact_messages, name='list-contact-messages'),
    path('dashboard/messages/view/<int:message_id>/', view_contact_message, name='view-contact-message'),
    path('dashboard/messages/delete/<int:message_id>/', delete_contact_message, name='delete-contact-message'),
    
    # CRUD Orders - para administradores
    path('dashboard/orders/', list_orders, name='list-orders'),
    path('dashboard/orders/view/<int:order_id>/', order_detail_admin, name='order-detail-admin'),
]