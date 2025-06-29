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
    path('dashboard/orders/<int:order_id>/marcar-entregada/', marcar_orden_entregada, name='marcar-orden-entregada'),
    
    # Vista de Bodega - para vendedores y bodegueros
    path('bodega/', vista_bodega, name='vista-bodega'),
    path('bodega/actualizar-stock/<int:product_id>/', actualizar_stock, name='actualizar-stock'),
    
    # Dashboard y funciones específicas para bodegueros
    path('bodeguero/', dashboard_bodeguero, name='dashboard-bodeguero'),
    path('bodeguero/ajuste-stock-masivo/', ajuste_stock_masivo, name='ajuste-stock-masivo'),
    path('bodeguero/reporte-inventario/', reporte_inventario, name='reporte-inventario'),
    path('bodeguero/historial-stock/', historial_stock, name='historial-stock'),
    
    # Dashboard específico para contadores
    path('contador/', dashboard_contador, name='dashboard-contador'),
    path('contador/historial-transacciones/', historial_transacciones_contador, name='historial-transacciones-contador'),
    path('contador/transaccion/<int:order_id>/', detalle_transaccion_contador, name='detalle-transaccion-contador'),
    path('contador/exportar-transacciones/', exportar_transacciones_contador, name='exportar-transacciones-contador'),
    
    # Informes mensuales para administradores
    path('dashboard/informes/', informes_mensuales, name='informes-mensuales'),
    path('dashboard/informes/pdf/', generar_informe_pdf, name='generar-informe-pdf'),
    
    # Gestión de Órdenes para Vendedores
    path('ordenes/', lista_ordenes_vendedor, name='lista-ordenes-vendedor'),
    path('ordenes/crear/', crear_orden_manual, name='crear-orden-manual'),
    path('ordenes/<int:order_id>/', detalle_orden_vendedor, name='detalle-orden-vendedor'),
    path('ordenes/<int:order_id>/eliminar-item/<int:item_id>/', eliminar_item_orden, name='eliminar-item-orden'),
]