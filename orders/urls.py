from django.urls import path
from orders import views

app_name = 'orders'

urlpatterns = [
    path('continuar/', views.continue_order_view, name='order_continue'),
    path('continuar/crear/', views.order_create_view, name='order_create'),
    path('lista/', views.order_list_view, name='order_list'),
    path('borrar/<int:order_id>/', views.order_delete_view, name='order_delete'),
    path('buscar/', views.order_search_view, name='order_search'),
    path('orden/<int:order_id>/qr/', views.order_qr_view, name='order_qr'),
    path('orden/<int:order_id>/cancel-stock/', views.order_cancel_stock_view, name='order_cancel_stock'),
    path('procesar-qr/', views.process_qr_view, name='process_qr'),
    path('no-quiero-ver/<int:order_id>/', views.order_donnot_show_view, name='order_donnot_show'),
    path('orden/<int:order_id>/detalle/', views.order_detail_view, name='order_detail'),
]
