"""StoreFlow settings: loopback demo defaults; production configuration is explicit."""
import os
import secrets
from pathlib import Path
from datetime import timedelta
from urllib.parse import urlparse, unquote

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = Path(os.environ.get("STOREFLOW_DATA_DIR", str(PROJECT_DIR / "runtime"))).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)
_secret = DATA_DIR / "secret.key"
if os.environ.get("STOREFLOW_SECRET_KEY"):
    SECRET_KEY = os.environ["STOREFLOW_SECRET_KEY"]
else:
    if not _secret.exists():
        try:
            with _secret.open("x", encoding="utf-8") as _file:
                _file.write(secrets.token_urlsafe(64))
        except FileExistsError:
            pass
    SECRET_KEY = _secret.read_text(encoding="utf-8").strip()
DEBUG = os.environ.get("STOREFLOW_DEBUG", "0") == "1"
DEMO_MODE = os.environ.get("STOREFLOW_DEMO_MODE", os.environ.get("STOREFLOW_DEMO", "1")) == "1"
ALLOWED_HOSTS = [x.strip() for x in os.environ.get("STOREFLOW_ALLOWED_HOSTS", "127.0.0.1,localhost,[::1],testserver").split(",") if x.strip()]
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "rest_framework", "rest_framework_simplejwt", "corsheaders", "django_filters", "drf_spectacular",
    "apps.users", "apps.employees", "apps.approvals", "apps.announcements", "apps.loans",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware", "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.loans.middleware.RequestLogMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [], "APP_DIRS": True,
    "OPTIONS": {"context_processors": ["django.template.context_processors.debug", "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "config.wsgi.application"
_database_url = os.environ.get("DATABASE_URL", "")
if _database_url:
    _db = urlparse(_database_url)
    if _db.scheme not in {"postgres", "postgresql"}:
        raise ValueError("DATABASE_URL must use postgres:// or postgresql://")
    DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql", "NAME": unquote(_db.path.lstrip("/")),
        "USER": unquote(_db.username or ""), "PASSWORD": unquote(_db.password or ""), "HOST": _db.hostname,
        "PORT": _db.port or 5432, "CONN_MAX_AGE": 0}}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("STOREFLOW_DB_PATH", str(DATA_DIR / "storeflow.sqlite3")), "OPTIONS": {"timeout": 20}}}
AUTH_USER_MODEL = "users.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["apps.loans.authentication.ActiveJWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "apps.loans.pagination.StandardPagination", "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_RATES": {"login": "30/min"},
}
SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(minutes=30), "REFRESH_TOKEN_LIFETIME": timedelta(days=1), "ROTATE_REFRESH_TOKENS": False, "CHECK_REVOKE_TOKEN": True}
SPECTACULAR_SETTINGS = {"TITLE": "StoreFlow 门店设备借用 API", "VERSION": "1.0.0", "SERVE_INCLUDE_SCHEMA": False,
    "ENUM_NAME_OVERRIDES": {"AssetStatusEnum": 'apps.loans.models.Asset.STATUS',
    "LoanStatusEnum": 'apps.loans.models.LoanRequest.STATUS',
    "HealthStatusEnum": ['ok', 'not_ready']}}
CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:5173", "http://localhost:5173"]
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/django-static/"
STATIC_ROOT = DATA_DIR / "staticfiles"
FRONTEND_DIST_DIR = Path(os.environ.get("STOREFLOW_FRONTEND_DIR", str(PROJECT_DIR / "frontend" / "dist"))).resolve()
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
LOGGING = {"version": 1, "disable_existing_loggers": False,
    "formatters": {"standard": {"format": "{asctime} {levelname} {name} {message}", "style": "{"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "standard"},
      "file": {"class": "logging.handlers.RotatingFileHandler", "filename": str(DATA_DIR / "app.log"),
               "maxBytes": 2 * 1024 * 1024, "backupCount": 3, "encoding": "utf-8", "formatter": "standard"}},
    "root": {"handlers": ["console", "file"], "level": "INFO"}}
