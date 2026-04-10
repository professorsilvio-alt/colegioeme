import os
from pathlib import Path
from dotenv import load_dotenv

# Apply Python 3.14 compatibility patches
from .patches import apply_patches
apply_patches()

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis de ambiente do arquivo .env
load_dotenv(BASE_DIR / '.env', override=True)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-eme-2026-robust-key-placeholder-must-change-in-prod')

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'SilvioFreitas.pythonanywhere.com,www.capelum.com,capelum.com,localhost,127.0.0.1').split(',')

CSRF_TRUSTED_ORIGINS_ENV = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'https://*.pythonanywhere.com,http://*.pythonanywhere.com,https://www.capelum.com,https://capelum.com,http://127.0.0.1:8000,http://localhost:8000'
)
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_ENV.split(',')]

# Cookie seguro apenas em HTTPS real (não no PythonAnywhere em HTTP)
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.SecurityHeadersMiddleware',
    'core.middleware.LoginRateLimitMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.ForcarTrocaSenhaMiddleware',
]

ROOT_URLCONF = 'eme_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.prof_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'eme_project.wsgi.application'

# Banco de dados
USE_MYSQL = os.environ.get('USE_MYSQL', 'False') == 'True'

if USE_MYSQL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'eme_db'),
            'USER': os.environ.get('DB_USER', 'eme_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'eme_password'),
            'HOST': os.environ.get('DB_HOST', 'db'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static_root'

# Configuração para o WhiteNoise servir arquivos estáticos de forma eficiente
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ──────────────────────────────────────────────
# SECURITY SETTINGS (PRODUCTION)
# ──────────────────────────────────────────────

# Security Headers (Global)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'

# Only enable these in production (when DEBUG is False and SSL is available)
if not DEBUG:
    # Proxy SSL Header (Necessário para PythonAnywhere/NGINX reconhecer HTTPS)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # HSTS
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # SSL Redirect
    SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', 'True') == 'True'
    
    # Secure Cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ──────────────────────────────────────────────
# SESSION
# ──────────────────────────────────────────────
# Sessão expira após 8 horas de inatividade (ideal para uso escolar)
SESSION_COOKIE_AGE = 8 * 60 * 60  # 8 horas em segundos
SESSION_SAVE_EVERY_REQUEST = True  # Renova o timer a cada request
SESSION_COOKIE_HTTPONLY = True      # JS não acessa o cookie de sessão

# ──────────────────────────────────────────────
# CONTENT SECURITY POLICY (básico)
# ──────────────────────────────────────────────
# Permite recursos apenas da própria origem e do Google Fonts (se usado no futuro)
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# ──────────────────────────────────────────────
# E-MAIL — GoDaddy SMTP (suporte@capelum.com)
# ──────────────────────────────────────────────
# Em desenvolvimento (DEBUG=True): imprime e-mails no terminal (sem servidor SMTP)
# Em produção (DEBUG=False): usa SMTP real configurado no .env
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST          = os.environ.get('EMAIL_HOST', 'smtpout.secureserver.net')
EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', 465))
EMAIL_USE_TLS       = os.environ.get('EMAIL_USE_TLS', 'False') == 'True'
EMAIL_USE_SSL       = os.environ.get('EMAIL_USE_SSL', 'True') == 'True'
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', 'suporte@capelum.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', 'Capelum <suporte@capelum.com>')
SERVER_EMAIL        = DEFAULT_FROM_EMAIL
EMAIL_TIMEOUT       = 10  # segundos — evita travamento em caso de falha SMTP
