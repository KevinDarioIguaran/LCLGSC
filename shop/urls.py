from django.urls import path
from . import views

app_name = 'shop' 

urlpatterns = [
    #Productos
    path('vender/', views.sell_view, name='sell'),
    path('editar/<int:product_id>/', views.edit_product_view, name='edit_product'),
    path('mis-productos/', views.list_my_products, name='list_my_products'),
    path('borrar/<int:product_id>/', views.delete_product_view, name='delete_product'),
    path('buscar-productos/', views.search_my_products, name="search_my_products"),
    path('detalle/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),

    #Órdene
    path('ordenes-pendientes/', views.pending_orders_view, name='pending_orders'),
    path('orden/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('orden/<int:order_id>/completada/', views.mark_order_completed_view, name='mark_order_completed'),

    #Carrito
    path('carrito/', views.cart_detail_view, name='cart_detail'),
    path('carrito/agregar/<int:product_id>/', views.cart_add_view, name='cart_add'),
    path('carrito/eliminar/<int:product_id>/', views.cart_remove_view, name='cart_remove'),
    path('carrito/actualizar/<int:product_id>/', views.cart_update, name='cart_update'),

    #Búsqueda
    path('buscar/', views.search_view, name='search'),
    path('buscar/categoria/<str:category>/', views.search_by_category_view, name='search_by_category'),

    #Vendedor
    path('recargar-credito/', views.seller_recharge_credit, name='seller_recharge_credit'),
    path('analizar-cooperativa/', views.seller_analytics_dashboard_view, name='seller_analytics_dashboard'),

]