from django.urls import path
from orders import views

app_name = 'orders'

urlpatterns = [
    path('continuar/', views.continue_order_view, name='order_continue'),
    path('continuar/crear/', views.order_create_view, name='order_create'),
    path('lista/', views.order_list_view, name='order_list'),
    path('borrar/<int:order_id>/', views.order_delete_view, name='order_delete'),
    path('buscar/', views.order_search_view, name='order_search'),

]
