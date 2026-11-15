"""Settings for the local QR code development sandbox."""

import json
import os
from pathlib import Path
from urllib.parse import urlsplit

from django import VERSION as DJANGO_VERSION

PROJECT_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = PROJECT_DIR.parent
SANDBOX_DATA_DIR = PROJECT_DIR / ".data"
SANDBOX_DATA_DIR.mkdir(exist_ok=True)
SANDBOX_BASE_URL = os.environ.get("SANDBOX_BASE_URL", "http://localhost:8000").rstrip(
    "/"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-swx69r7+kdw60)m8n3*uaff0kgbkaw+4^ou2a_y0km)pgev01#"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

INSTALLED_APPS = [
    "home",
    "wagtail_qrcode",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    "django_filters",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            PROJECT_DIR / "templates",
        ],
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": SANDBOX_DATA_DIR / "db.sqlite3",
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
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


LANGUAGE_CODE = "en-gb"

TIME_ZONE = "Europe/London"

STATICFILES_DIRS = [
    PROJECT_DIR / "static",
]

STATIC_ROOT = SANDBOX_DATA_DIR / "static"
STATIC_URL = "/static/"

MEDIA_ROOT = SANDBOX_DATA_DIR / "media"
MEDIA_URL = "/media/"

WAGTAIL_SITE_NAME = "Wagtail QRcode Sandbox"

base_url = urlsplit(SANDBOX_BASE_URL)
if (
    base_url.scheme not in {"http", "https"}
    or not base_url.hostname
    or base_url.path not in {"", "/"}
    or base_url.query
    or base_url.fragment
    or base_url.username
):
    raise ValueError("SANDBOX_BASE_URL must be an http(s) origin without a path")
SANDBOX_HOST = base_url.hostname
SANDBOX_PORT = base_url.port or (443 if base_url.scheme == "https" else 80)
allowed_host = SANDBOX_HOST if ":" not in SANDBOX_HOST else f"[{SANDBOX_HOST}]"
ALLOWED_HOSTS = list(dict.fromkeys([*ALLOWED_HOSTS, allowed_host]))
CSRF_TRUSTED_ORIGINS = [SANDBOX_BASE_URL]
WAGTAILADMIN_BASE_URL = SANDBOX_BASE_URL
WAGTAIL_QR_CODE_BASE_URL = SANDBOX_BASE_URL
DEFAULT_FROM_EMAIL = "sandbox@example.test"

WAGTAIL_QR_CODE = json.loads(os.environ.get("WAGTAIL_QR_CODE", "{}"))
if "WAGTAIL_QRCODE_EMAIL_SUBJECT" in os.environ:
    WAGTAIL_QRCODE_EMAIL_SUBJECT = os.environ["WAGTAIL_QRCODE_EMAIL_SUBJECT"]
if "WAGTAIL_QRCODE_EMAIL_BODY" in os.environ:
    WAGTAIL_QRCODE_EMAIL_BODY = os.environ["WAGTAIL_QRCODE_EMAIL_BODY"]

# Capture messages locally, preserving MIME attachments.
if DJANGO_VERSION >= (6, 1):
    MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.filebased.EmailBackend",
            "OPTIONS": {"file_path": SANDBOX_DATA_DIR / "emails"},
        }
    }
else:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = SANDBOX_DATA_DIR / "emails"

TEST_RUNNER = "home.runner.SandboxTestRunner"
