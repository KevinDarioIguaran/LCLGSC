from django.urls import path
from . import views
app_name = 'shop' 

urlpatterns = [
    path('sell/', views.sell_view, name='sell'),
    path('detail/<int:id>/<slug:slug>/', views.product_detail,name='product_detail'),
    path('search/', views.search_view, name='search'),
    path('search/category/<str:category>', views.search_by_category_view, name='search_by_category'), 
    path('cart/', views.cart_detail_view, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add_view, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove_view, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
]
