from pathlib import Path
import os
from dotenv import load_dotenv

# Base dir
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# -------------------------------------------------
# SECURITY
# -------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-change")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in ("1", "true", "yes")

# Allow Render, Vercel frontend, local dev
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

# -------------------------------------------------
# APPS
# -------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # third-party
    "corsheaders",

    # your app
    "api",
]

# -------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",          # CORS first
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",     # Static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

# -------------------------------------------------
# TEMPLATES
# -------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "backend.wsgi.application"

# -------------------------------------------------
# DATABASE (SQLite OK for Render free tier)
# -------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# -------------------------------------------------
# PASSWORD VALIDATION
# -------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------------------
# INTERNATIONALIZATION
# -------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------
# STATIC FILES (Render Deployment)
# -------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------------------------------
# CORS SETTINGS (FINAL FIXED VERSION)
# -------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    "https://realestate-analyzer-8olm.vercel.app",     # Your Vercel frontend
    "https://realestate-analyzer-vc9k.onrender.com",   # Your backend domain
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

# IMPORTANT: REMOVE CORS_ALLOW_ALL_ORIGINS (causes conflict)
# DO NOT ADD IT AGAIN.

# -------------------------------------------------
# ENV VARS
# -------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print("DEBUG: GROQ KEY present? ", bool(GROQ_API_KEY))

# -------------------------------------------------
# DEFAULT PRIMARY KEY TYPE
# -------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
