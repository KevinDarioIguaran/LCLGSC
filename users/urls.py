from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'users' 

urlpatterns = [
    path("perfil/", views.show_account_view, name="show_account"),
    path("perfil/login/", views.login_view, name="login"),
    path("perfil/signup/", views.signup_view, name="signup"), 
    path("perfil/cambiar-contraseña/", views.change_password_view, name="change_password"),
    path("perfil/crear-contraseña/", views.set_password, name="set_password"),
    path("perfil/eliminar-cuenta/", views.delete_account_view, name="delete_account"),
    path("perfil/logout/", views.logout_view, name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)