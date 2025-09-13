from django.urls import path
from home import views
from django.conf import settings
from django.conf.urls.static import static




app_name = 'home' 


urlpatterns = [
    path('', views.home_view, name='home'),
    path('ofertas/', views.offers_view, name='offers'),
    path('mas-vendidos/', views.best_sellers_view, name='best_sellers'),
    path('atencion-al-cliente/', views.customer_service_view, name='customer_service'),
    path('acerca-de/', views.about_view, name='about'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
