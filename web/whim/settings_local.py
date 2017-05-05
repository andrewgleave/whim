from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'whim',
        'USER': 'whim',
        'PASSWORD': 'whim',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}