"""
Django settings for books project.

Generated by 'django-admin startproject' using Django 2.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

ON_HEROKU = True if 'DATABASE_URL' in os.environ else False

# SECURITY WARNING: don't run with debug turned on in production!
if ON_HEROKU:
    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = False
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = os.environ['SECRET_KEY']
else:
    DEBUG = True
    SECRET_KEY = '#k-b7j1ucvc2#w)lrmw0^pq@2v^n#%4x7^%8vkyu@r4e4+0ngv'


ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'readseek.org', 'readseek.herokapp.com',
                 'www.readseek.org']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.postgres',  # Required for Postgres search.
    'rest_framework',
    'corsheaders',
    # 'webpack_loader',

    # 'main.apps.AppConfig', # This is the modern way of doing it, but I get"
    #"django.core.exceptions.ImproperlyConfigured: 'main.apps.AppConfig' must "
    #supply a name attribute."
    'main'
]

"""
CorsMiddleware should be placed as high as possible, especially before any 
middleware that can generate responses such as Django's CommonMiddleware or 
Whitenoise's WhiteNoiseMiddleware. If it is not before, it will not be able 
to add the CORS headers to these responses.
"""

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'books.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Is this required?
        'DIRS': [os.path.join(BASE_DIR, "templates"), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'books.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
LOCAL_DB = 'postgres://david:test@localhost:5432/books'

DATABASES = {'default': dj_database_url.config(default=LOCAL_DB)}

# For connecting to Heroku's database from a local machine:
# from private import HEROKU_DB_URL
# DATABASES = {'default': dj_database_url.config(default=HEROKU_DB_URL)}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

# https://github.com/kennethreitz/dj-static
STATIC_ROOT = 'staticfiles'
# STATIC_URL = '/frontend/build/static/'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    # os.path.join(BASE_DIR, 'frontend/build/static'),
)


# todo look up what this is for
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
}

CORS_ORIGIN_ALLOW_ALL = True
