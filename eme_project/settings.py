import os
from pathlib import Path
from dotenv import load_dotenv

# Apply Python 3.14 compatibility patches
from .patches import apply_patches
apply_patches()

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis de ambiente do arquivo .env
load_dotenv(BASE_DIR / '.env', override=True)

# Em produção, a SECRET_KEY DEVE ser definida via variável de ambiente.
# Se não estiver definida e DEBUG=False, o sistema irá crashar imediatamente.
_secret = os.environ.get('DJANGO_SECRET_KEY', '')
if not _secret and os.environ.get('DJANGO_DEBUG', 'True') != 'True':
    raise RuntimeError(
        'DJANGO_SECRET_KEY não definida! Defina uma chave secreta forte '
        'na variável de ambiente antes de rodar em produção.'
    )
SECRET_KEY = _secret or 'django-insecure-dev-only-key-DO-NOT-USE-IN-PRODUCTION'

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
    'core.middleware.EscolaMiddleware',
    'core.middleware.AnoLetivoMiddleware',
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
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static_root'

# Arquivos de mídia (uploads de usuário, ex.: fotos de alunos)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuração para o WhiteNoise servir arquivos estáticos de forma eficiente
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
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

# ──────────────────────────────────────────────
# RECAPTCHA v3 — Google
# ──────────────────────────────────────────────
RECAPTCHA_SITE_KEY   = os.environ.get('RECAPTCHA_SITE_KEY', '').strip()
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', '').strip()
# Score mínimo aceitável (0.0 = bot certo, 1.0 = humano certo). 0.5 é o padrão Google.
RECAPTCHA_MIN_SCORE = 0.5
BYPASS_RECAPTCHA = os.environ.get('BYPASS_RECAPTCHA', 'False') == 'True'

# ──────────────────────────────────────────────
# ADMINS — alertas automáticos por e-mail em erros 500
# ──────────────────────────────────────────────
# Django envia e-mail para cada endereço listado aqui sempre que
# ocorrer uma exceção não tratada (erro 500) em produção.
# Requer DEBUG=False e SERVER_EMAIL configurado corretamente.
ADMINS = [
    ('Capelum Admin', os.environ.get('ADMIN_EMAIL', 'suporte@capelum.com')),
]
MANAGERS = ADMINS  # também recebe notificações de links quebrados (404 recorrentes)

# ──────────────────────────────────────────────
# LOGGING — registro estruturado de eventos
# ──────────────────────────────────────────────
# Em desenvolvimento (DEBUG=True): apenas console, nível INFO
# Em produção (DEBUG=False):
#   • Arquivo rotativo diário em /var/log/capelum/app.log (30 dias de histórico)
#   • Erros Django também disparam e-mail via ADMINS (handler 'mail_admins')
#   • Nível WARNING no arquivo para reduzir ruído; ERROR no e-mail
LOG_DIR = os.environ.get('LOG_DIR', str(Path.home() / 'logs' / 'capelum'))
os.makedirs(LOG_DIR, exist_ok=True)  # cria automaticamente se não existir

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name} — {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },

    'handlers': {
        # Console — ativo apenas em desenvolvimento
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_true'],
        },
        # Arquivo rotativo diário — ativo apenas em produção
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'app.log'),
            'when': 'midnight',
            'backupCount': 30,        # mantém 30 dias de logs
            'encoding': 'utf-8',
            'formatter': 'verbose',
            'filters': ['require_debug_false'],
        },
        # E-mail para ADMINS — apenas erros críticos em produção
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_false'],
            'include_html': False,  # Evita expor dados sensíveis de sessão nos e-mails de erro
        },
    },

    'loggers': {
        # Logger raiz da aplicação Capelum/EME
        'core': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        # Erros do Django (500, templates, etc.)
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        # Requests HTTP — apenas em produção, nível WARNING
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Queries SQL lentas (>300ms) — apenas em produção
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
