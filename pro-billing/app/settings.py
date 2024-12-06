from os import environ
from pathlib import Path

import dj_database_url
import redis
from dotenv import load_dotenv
from forgepro.default_settings import FORGEPRO_APPS, FORGEPRO_MIDDLEWARE

# Load environment variables from repo .env file (only exists in development)
load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = environ.get("DEBUG", "false").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    # django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
    "widget_tweaks",
    "teams",
    "users",
    "projects",
    "packages",
    "django_hosts",
] + FORGEPRO_APPS

MIDDLEWARE = (
    [
        "django_hosts.middleware.HostsRequestMiddleware",
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]
    + FORGEPRO_MIDDLEWARE
    + [
        "django_hosts.middleware.HostsResponseMiddleware",
    ]
)

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

if (BASE_DIR / "wsgi.py").exists():
    WSGI_APPLICATION = "wsgi.application"
else:
    WSGI_APPLICATION = "forgecore.default_files.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.parse(
        environ["DATABASE_URL"], conn_max_age=environ.get("DATABASE_CONN_MAX_AGE", 600)
    )
}

# Caching
# https://docs.djangoproject.com/en/4.0/topics/cache/
if environ.get("REDIS_URL", ""):
    if environ["REDIS_URL"].startswith("rediss://"):
        options = {
            "connection_class": redis.SSLConnection,
            "ssl_cert_reqs": environ.get("REDIS_SSL_CERT_REQS", "required"),
        }
    else:
        options = {}

    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": environ["REDIS_URL"],
            "OPTIONS": options,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Chicago"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [BASE_DIR / "static"]

if not DEBUG:
    # Enable whitenoise for staticfiles
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    # Should be 2nd, after security middleware
    MIDDLEWARE = (
        MIDDLEWARE[:1] + ["whitenoise.middleware.WhiteNoiseMiddleware"] + MIDDLEWARE[1:]
    )


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Custom user model and authentication flows

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "auth.EmailModelBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# URLs and CSRF

BASE_URL = environ["BASE_URL"]

if "CSRF_TRUSTED_ORIGINS" in environ:
    CSRF_TRUSTED_ORIGINS = environ[
        "CSRF_TRUSTED_ORIGINS"
    ].split()  # whitespace separated
else:
    CSRF_TRUSTED_ORIGINS = [BASE_URL]


# Email

if "EMAIL_HOST" in environ:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = environ["EMAIL_HOST"]
    EMAIL_PORT = environ.get("EMAIL_PORT", 587)
    EMAIL_HOST_USER = environ["EMAIL_HOST_USER"]
    EMAIL_HOST_PASSWORD = environ["EMAIL_HOST_PASSWORD"]
    DEFAULT_FROM_EMAIL = environ["DEFAULT_FROM_EMAIL"]
elif DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Form rendering

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"


# Production settings

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    X_FRAME_OPTIONS = "DENY"

# So we can use {% if debug %} in templates
INTERNAL_IPS = ["127.0.0.1"]

# Logging settings

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(levelname)s] %(message)s",
        }
    },
    "filters": {
        "exclude_common_urls": {
            "()": "forgelogging.filters.ExcludeCommonURLsFilter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "filters": ["exclude_common_urls"],
        },
        "app": {
            "handlers": ["console"],
            "level": environ.get("APP_LOG_LEVEL", "INFO"),
        },
    },
}

STRIPE_PRICE_ID = environ["STRIPE_PRICE_ID"]

GITHUB_APP_PRIVATE_KEY = environ["GITHUB_APP_PRIVATE_KEY"]
GITHUB_APP_ID = int(environ["GITHUB_APP_ID"])
GITHUB_APP_INSTALLATION_ID = int(environ["GITHUB_APP_INSTALLATION_ID"])

ROOT_HOSTCONF = "hosts"
DEFAULT_HOST = "billing"
