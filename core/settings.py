import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv(dotenv_path=".env.dev")

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "changeme")

DEBUG = os.getenv("DEBUG", "0") == "1"

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost").split(" ")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # 3rd-party
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "corsheaders",

    # local apps
    "accounts",
    "billing",
    "generator",
    "frontend",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "backend" / "frontend" / "templates"],
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

WSGI_APPLICATION = "core.wsgi.application"

# Database
DATABASES = {
    "default": dj_database_url.config(default=os.getenv("DATABASE_URL"))
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", "English"),
    ("pt", "Português"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "backend" / "static",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "accounts.User"

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Email backend (console for now)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
DEFAULT_FROM_EMAIL = "your_verified_sender@example.com"

#DEFAULT_FROM_EMAIL = "no-reply@yourdomain.com" (not yet done)

REST_AUTH_SERIALIZERS = {
    "LOGIN_SERIALIZER": "accounts.serializers.CustomLoginSerializer"
}



# Allauth / dj-rest-auth settings
SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # or "optional"

ACCOUNT_SIGNUP_FIELDS = ['email']


# Oauth2

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

LOGIN_REDIRECT_URL = "/"

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")
SOCIALACCOUNT_LOGIN_ON_GET = True


REST_AUTH_REGISTER_SERIALIZERS = {
    "REGISTER_SERIALIZER": "accounts.serializers.CustomRegisterSerializer"
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
]

CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]
CSRF_COOKIE_HTTPONLY = False   # allow JS to read cookie for HTMX
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"



