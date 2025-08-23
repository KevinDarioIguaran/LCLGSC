from django.urls import path
from . import views

app_name = 'shop' 

urlpatterns = [
    path('vender/', views.sell_view, name='sell'),
    path('detalle/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('buscar/', views.search_view, name='search'),
    path('buscar/categoria/<str:category>/', views.search_by_category_view, name='search_by_category'), 

    path('carrito/', views.cart_detail_view, name='cart_detail'),
    path('carrito/agregar/<int:product_id>/', views.cart_add_view, name='cart_add'),
    path('carrito/eliminar/<int:product_id>/', views.cart_remove_view, name='cart_remove'),
    path('carrito/actualizar/<int:product_id>/', views.cart_update, name='cart_update'),
]

