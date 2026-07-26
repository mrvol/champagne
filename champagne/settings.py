from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-dev-key'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'mp',
    'person',
    'address',
    'company',
    'goods',
    'order',
    'payment',
    'review',
    'transaction',
    'warehouse',
    'cart',
    'price',
    'discount',
    'invite',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'person.middleware.UserLanguageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'champagne.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'mp.context_processors.staff_nav',
            ],
        },
    },
]

WSGI_APPLICATION = 'champagne.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'person.User'

LOGIN_URL = 'login'

LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
    ('ru', 'Русский'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# No real SMTP configured for this project yet; emails print to the console/log.
# Swap for 'django.core.mail.backends.smtp.EmailBackend' + EMAIL_HOST/PORT/etc. in production.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Champagne <no-reply@champagne.example>'
SITE_BASE_URL = 'http://localhost:8989'
ADMIN_NOTIFICATION_EMAILS = ['admin@champagne.example']
