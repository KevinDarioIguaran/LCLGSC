from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-=nr-6uxd$0tgo56d+i0pm@x(^gv&h4ty)*_8yjkmnmujf+kf@+'

DEBUG = True


ALLOWED_HOSTS = [
    '*'
]

CSRF_TRUSTED_ORIGINS = [
  #  "http://192.168.1.6:9000",
    "http://localhost:9000",
    "http://127.0.0.1:9000",
    "https://for-decent-judges-matters.trycloudflare.com",
    "http://192.168.1.20:8000"
    
]



# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    "django_extensions",

    'shop',
    'users',
    'home',
    'orders',
    'blocks',


]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'blocks.middleware.blocks_middleware.BlocksMiddleware',



]

ROOT_URLCONF = 'luis_carlos_cooperativa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],  
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'luis_carlos_cooperativa.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/


STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Configuración archivos subidos 
FILE_UPLOAD_MAX_MEMORY_SIZE = 1 * 1024 * 1024 * 1024  # 1 GB
DATA_UPLOAD_MAX_MEMORY_SIZE = 1 * 1024 * 1024 * 1024  # 1 GB

MAX_FILE_SIZE_IMAGES = 5 * 1024 * 1024  # 5 MB
VALID_EXTENSIONS_IMAGES = {'jpg', 'jpeg', 'png', 'webp'}


AUTH_USER_MODEL = 'users.CustomUser'





LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'home:home'



JAZZMIN_SETTINGS = {
    "site_title": "Café L.C.G.S Administración",
    "site_header": "Café L.C.G.S Administración",
    "site_brand": "Café L.C.G.S",

    "welcome_sign": "Bienvenido a la Administración de Café L.C.G.S",
    "copyright": "Café L.C.G.S 2025",

    "topmenu_links": [
        {"name": "Sitio normal", "url": "home:home"},
    ],

    "show_sidebar": True,
    "navigation_expanded": True,

    "site_logo": "assets/icons/favicon.ico",

    "custom_links": {
        "books": [{
            "name": "Make Messages",
            "url": "make_messages",
            "icon": "fas fa-comments",
            "permissions": ["books.view_book"]
        }]
    },

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.Group": "fas fa-users",
        "admin.LogEntry": "fas fa-history",

        "users.CustomUser": "fas fa-user-circle",


        "shop.Category": "fas fa-tags",
        "shop.Product": "fas fa-box-open",
        "shop.Favorite": "fas fa-heart",
        "shop.Cart": "fas fa-shopping-cart",
        "shop.ShowBestOffers": "fa-solid fa-chart-simple",
        "shop.RechargeLogs": "fa-solid fa-chart-column", 

        "blocks.ActiveSite": "fa-solid fa-plug",
        "blocks.WeekendDay": "fa-solid fa-calendar",


        "orders.Order": "fas fa-shopping-basket ",
    },
}
