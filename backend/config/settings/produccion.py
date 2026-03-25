from .base import *  # noqa: F403, F401

DEBUG = False
ALLOWED_HOSTS = ['64.227.110.12', 'app.confeccionesunoa.com']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'confecciones',
        'USER': 'confecciones',
        'PASSWORD': 'Confecciones2026!',
        'HOST': '64.227.110.12',
        'PORT': '5432',
    }
}


MEDIA_ROOT = '/media/'  # Docker volume
STATIC_ROOT = "/public/"  # Docker volume
