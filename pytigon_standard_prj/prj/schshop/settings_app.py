import os
import sys
import json
from urllib.parse import urlparse

PRJ_TITLE = "Shop"
PRJ_NAME = "schshop"
THEMES = ["tablet_modern", "tablet_modern", "smartfon_standard"]

_lp = os.path.dirname(os.path.abspath(__file__))

if "PYTIGON_ROOT_PATH" in os.environ:
    _rp = os.environ["PYTIGON_ROOT_PATH"]
else:
    _rp = os.path.abspath(os.path.join(_lp, "..", ".."))

if not _lp in sys.path:
    sys.path.insert(0, _lp)
if not _rp in sys.path:
    sys.path.insert(0, _rp)

from pytigon_lib import init_paths

init_paths(PRJ_NAME, _lp)

from pytigon_lib.schdjangoext.django_init import get_app_config
from pytigon_lib.schtools.platform_info import platform_name

from pytigon.schserw.settings import *

from apps import APPS, APPS_EXT, PUBLIC

try:
    from global_db_settings import setup_databases
except ImportError:
    setup_databases = None

LOCAL_ROOT_PATH = os.path.abspath(os.path.join(_lp, ".."))
ROOT_PATH = _rp
URL_ROOT_PREFIX = ""
if not LOCAL_ROOT_PATH in sys.path:
    sys.path.append(LOCAL_ROOT_PATH)

if ENV("PUBLISH_IN_SUBFOLDER"):
    if ENV("PUBLISH_IN_SUBFOLDER") == "_":
        URL_ROOT_FOLDER = PRJ_NAME
    else:
        URL_ROOT_FOLDER = ENV("PUBLISH_IN_SUBFOLDER")
    URL_ROOT_PREFIX = URL_ROOT_FOLDER + "/"
    STATIC_URL = URL_ROOT_FOLDER + "/static/"
    MEDIA_URL = URL_ROOT_FOLDER + "/site_media/"
    MEDIA_URL_PROTECTED = URL_ROOT_FOLDER + "/site_media_protected/"
    SESSION_COOKIE_NAME = URL_ROOT_FOLDER.lower() + "_sessionid"
    CSRF_COOKIE_NAME = URL_ROOT_FOLDER.lower() + "_csrftoken"

MEDIA_ROOT = os.path.join(
    os.path.join(DATA_PATH, URL_ROOT_FOLDER if URL_ROOT_FOLDER else PRJ_NAME), "media"
)
UPLOAD_PATH = os.path.join(MEDIA_ROOT, "upload")

import ast
import django
from django.contrib.messages import constants as messages
from django_prices.utils.formatting import get_currency_fraction
from django.utils.translation import gettext_lazy as _

from django.urls import re_path
import django.conf.urls

django.conf.urls.url = re_path

from django.utils.encoding import smart_str

django.utils.encoding.smart_text = smart_str

from django.utils.encoding import force_str

django.utils.encoding.force_text = force_str

from django.utils.translation import gettext_lazy

django.utils.translation.ugettext_lazy = gettext_lazy

from django.utils.translation import gettext

django.utils.translation.ugettext = gettext

from django.forms.boundfield import BoundField

django.forms.forms.BoundField = BoundField


def get_list(text):
    return [item.strip() for item in text.split(",")]


def get_bool_from_env(name, default_value):
    if name in os.environ:
        value = os.environ[name]
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            raise ValueError("{} is an invalid value for {}".format(value, name)) from e
    return default_value


PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))
sys.path.append(os.path.join(PROJECT_ROOT, "ext_lib"))

GETPAID_ORDER_MODEL = "order.Order"
GETPAID_PAYMENT_MODEL = "payment.Payment"

GETPAID_BACKEND_SETTINGS = {
    "getpaid_payu": {
        # take these from your merchant panel:
        "pos_id": "2838469",
        "second_key": "d322edec57a08a550d759a8b6914d292",
        "oauth_id": "2838469",
        "oauth_secret": "e370c2094f5bdba0d908a4b274605abf",
    },
}

# ROOT_URLCONF = "saleor.urls"

# WSGI_APPLICATION = "saleor.wsgi.application"

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS

ALLOWED_CLIENT_HOSTS = get_list(
    os.environ.get("ALLOWED_CLIENT_HOSTS", "localhost,127.0.0.1")
)

INTERNAL_IPS = get_list(os.environ.get("INTERNAL_IPS", "127.0.0.1"))

TIME_ZONE = "Europe/Warsaw"
LANGUAGE_CODE = "pl"
LANGUAGES = [
    ("pl", _("Polish")),
]

LOCALE_PATHS = [os.path.join(PROJECT_ROOT, "locale")]
USE_I18N = True
USE_L10N = True
USE_TZ = True

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

EMAIL_HOST = "PLSMTP11.crhem.pl"
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

DEFAULT_FROM_EMAIL = "sklep@polbruk.pl"

EMAIL_BACKEND = "mailer.backend.DbBackend"
ENABLE_SSL = True

context_processors = [
    # "django.contrib.auth.context_processors.auth",
    # "django.template.context_processors.debug",
    # "django.template.context_processors.i18n",
    # "django.template.context_processors.media",
    # "django.template.context_processors.static",
    # "django.template.context_processors.tz",
    # "django.contrib.messages.context_processors.messages",
    # "django.template.context_processors.request",
    "saleor.core.context_processors.default_currency",
    "saleor.checkout.context_processors.checkout_counter",
    "saleor.core.context_processors.search_enabled",
    "saleor.site.context_processors.site",
    "social_django.context_processors.backends",
    "social_django.context_processors.login_redirect",
    "shop.context_processors.in_frame",
]

TEMPLATES[0]["DIRS"].insert(
    0, os.path.join(PRJ_PATH, PRJ_NAME, "prjlib", "ext_lib", "templates")
)
TEMPLATES[0]["DIRS"].insert(
    1, os.path.join(PRJ_PATH, PRJ_NAME, "prjlib", "saleor", "templates")
)
TEMPLATES[0]["OPTIONS"]["context_processors"] += context_processors

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get("SECRET_KEY")
SECRET_KEY = "AnawaAnawa1"

MIDDLEWARE += [
    # "django.contrib.sessions.middleware.SessionMiddleware",
    # "django.middleware.security.SecurityMiddleware",
    # "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    # "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django_babel.middleware.LocaleMiddleware",
    "saleor.core.middleware.discounts",
    "saleor.core.middleware.google_analytics",
    "saleor.core.middleware.country",
    "saleor.core.middleware.currency",
    "saleor.core.middleware.site",
    "saleor.core.middleware.extensions",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "impersonate.middleware.ImpersonateMiddleware",
    # "saleor.graphql.middleware.jwt_middleware",
    # "saleor.graphql.middleware.service_account_middleware",
    # SCH++
    "big_company.middleware.profile",
    # "sync.schjwt.JWTUserMiddleware",
    # SCH--
]

INSTALLED_APPS = [
    # External apps that need to go before django's
    "storages",
] + INSTALLED_APPS

INSTALLED_APPS += [
    "django.contrib.postgres",
    # Local apps
    "saleor.extensions",
    "saleor.account",
    "saleor.discount",
    "saleor.giftcard",
    "saleor.product",
    "saleor.checkout",
    "saleor.core",
    # "saleor.graphql",
    "saleor.menu",
    "saleor.order",
    "saleor.dashboard",
    "saleor.seo",
    "saleor.shipping",
    "saleor.search",
    "saleor.site",
    "saleor.data_feeds",
    "saleor.page",
    "saleor.payment",
    "saleor.webhook",
    # External apps
    "versatileimagefield",
    # "django_babel",
    "bootstrap4",
    "django_measurement",
    "django_prices",
    "django_prices_openexchangerates",
    "django_prices_vatlayer",
    "graphene_django",
    "mptt",
    "webpack_loader",
    "social_django",
    "django_countries",
    "django_filters",
    "impersonate",
    "phonenumber_field",
    "captcha",
    # SCH++
    "big_company",
    #'polbruk.sync',
    "getpaid",
    "getpaid_payu",
    "polbruk",
    # SCH--
]

# INSTALLED_APPS.remove("allauth.account")

LOGIN_URL = "/account/login/"

AUTH_USER_MODEL = "account.User"
ACCOUNT_USER_MODEL_USERNAME_FIELD = "email"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
CAN_RESET_PASSWORD = True
CAN_CHANGE_PASSWORD = True
CAN_REGISTER = True


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    }
]

DEFAULT_COUNTRY = os.environ.get("DEFAULT_COUNTRY", "PL")
DEFAULT_CURRENCY = os.environ.get("DEFAULT_CURRENCY", "PLN")
DEFAULT_DECIMAL_PLACES = get_currency_fraction(DEFAULT_CURRENCY)
DEFAULT_MAX_DIGITS = 12
DEFAULT_CURRENCY_CODE_LENGTH = 3
DEFAULT_MAX_EMAIL_DISPLAY_NAME_LENGTH = 78
AVAILABLE_CURRENCIES = [DEFAULT_CURRENCY]

OPENEXCHANGERATES_API_KEY = os.environ.get("OPENEXCHANGERATES_API_KEY")

# VAT configuration
# Enabling vat requires valid vatlayer access key.
# If you are subscribed to a paid vatlayer plan, you can enable HTTPS.
# SCH++
# VATLAYER_ACCESS_KEY = os.environ.get("VATLAYER_ACCESS_KEY")
VATLAYER_ACCESS_KEY = "4112c938306c9f0d1a778f3196e329bd"
# SCH--
VATLAYER_USE_HTTPS = get_bool_from_env("VATLAYER_USE_HTTPS", False)

# Avatax supports two ways of log in - username:password or account:license
AVATAX_USERNAME_OR_ACCOUNT = os.environ.get("AVATAX_USERNAME_OR_ACCOUNT")
AVATAX_PASSWORD_OR_LICENSE = os.environ.get("AVATAX_PASSWORD_OR_LICENSE")
AVATAX_USE_SANDBOX = get_bool_from_env("AVATAX_USE_SANDBOX", DEBUG)
AVATAX_COMPANY_NAME = os.environ.get("AVATAX_COMPANY_NAME", "DEFAULT")
AVATAX_AUTOCOMMIT = get_bool_from_env("AVATAX_AUTOCOMMIT", False)

ACCOUNT_ACTIVATION_DAYS = 3

LOGIN_REDIRECT_URL = "home"

GOOGLE_ANALYTICS_TRACKING_ID = os.environ.get("GOOGLE_ANALYTICS_TRACKING_ID")


def get_host():
    from django.contrib.sites.models import Site

    return Site.objects.get_current().domain


PAYMENT_HOST = get_host

PAYMENT_MODEL = "order.Payment"

SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

MESSAGE_TAGS = {messages.ERROR: "danger"}

LOW_STOCK_THRESHOLD = 10
MAX_CHECKOUT_LINE_QUANTITY = int(os.environ.get("MAX_CHECKOUT_LINE_QUANTITY", 50))

PAGINATE_BY = 16
DASHBOARD_PAGINATE_BY = 30
DASHBOARD_SEARCH_LIMIT = 5

bootstrap4 = {
    "set_placeholder": False,
    "set_required": False,
    "success_css_class": "",
    "form_renderers": {"default": "saleor.core.utils.form_renderer.FormRenderer"},
}

TEST_RUNNER = "tests.runner.PytestTestRunner"

ALLOWED_HOSTS = get_list(os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1"))

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Amazon S3 configuration
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_LOCATION = os.environ.get("AWS_LOCATION", "")
AWS_MEDIA_BUCKET_NAME = os.environ.get("AWS_MEDIA_BUCKET_NAME")
AWS_MEDIA_CUSTOM_DOMAIN = os.environ.get("AWS_MEDIA_CUSTOM_DOMAIN")
AWS_QUERYSTRING_AUTH = get_bool_from_env("AWS_QUERYSTRING_AUTH", False)
AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_STATIC_CUSTOM_DOMAIN")
AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL", None)
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_DEFAULT_ACL = os.environ.get("AWS_DEFAULT_ACL", None)

# Google Cloud Storage configuration
GS_PROJECT_ID = os.environ.get("GS_PROJECT_ID")
GS_STORAGE_BUCKET_NAME = os.environ.get("GS_STORAGE_BUCKET_NAME")
GS_MEDIA_BUCKET_NAME = os.environ.get("GS_MEDIA_BUCKET_NAME")
GS_AUTO_CREATE_BUCKET = get_bool_from_env("GS_AUTO_CREATE_BUCKET", False)

# If GOOGLE_APPLICATION_CREDENTIALS is set there is no need to load OAuth token
# See https://django-storages.readthedocs.io/en/latest/backends/gcloud.html
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    GS_CREDENTIALS = os.environ.get("GS_CREDENTIALS")

if AWS_STORAGE_BUCKET_NAME:
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
elif GS_STORAGE_BUCKET_NAME:
    STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"

if AWS_MEDIA_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = "saleor.core.storages.S3MediaStorage"
    THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE
elif GS_MEDIA_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = "saleor.core.storages.GCSMediaStorage"
    THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

VERSATILEIMAGEFIELD_RENDITION_KEY_SETS = {
    "products": [
        ("product_gallery", "thumbnail__540x540"),
        ("product_gallery_2x", "thumbnail__1080x1080"),
        ("product_small", "thumbnail__60x60"),
        ("product_small_2x", "thumbnail__120x120"),
        ("product_list", "thumbnail__255x255"),
        ("product_list_2x", "thumbnail__510x510"),
    ],
    "background_images": [("header_image", "thumbnail__1080x440")],
    "user_avatars": [("default", "thumbnail__445x445")],
}

VERSATILEIMAGEFIELD_SETTINGS = {
    # Images should be pre-generated on Production environment
    "create_images_on_demand": get_bool_from_env("CREATE_IMAGES_ON_DEMAND", DEBUG),
    "jpeg_resize_quality": 90,
}

PLACEHOLDER_IMAGES = {
    60: "images/placeholder60x60.png",
    120: "images/placeholder120x120.png",
    255: "images/placeholder255x255.png",
    540: "images/placeholder540x540.png",
    1080: "images/placeholder1080x1080.png",
}

DEFAULT_PLACEHOLDER = "images/placeholder255x255.png"

WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "BUNDLE_DIR_NAME": "assets/",
        "STATS_FILE": os.path.join(PROJECT_ROOT, "webpack-bundle.json"),
        "POLL_INTERVAL": 0.1,
        "IGNORE": [r".+\.hot-update\.js", r".+\.map"],
    }
}


LOGOUT_ON_PASSWORD_CHANGE = False

# SEARCH CONFIGURATION
DB_SEARCH_ENABLED = True

# support deployment-dependant elastic environment variable
ES_URL = (
    os.environ.get("ELASTICSEARCH_URL")
    or os.environ.get("SEARCHBOX_URL")
    or os.environ.get("BONSAI_URL")
)

ENABLE_SEARCH = bool(ES_URL) or DB_SEARCH_ENABLED  # global search disabling

SEARCH_BACKEND = "saleor.search.backends.postgresql"

if ES_URL:
    SEARCH_BACKEND = "saleor.search.backends.elasticsearch"
    INSTALLED_APPS.append("django_elasticsearch_dsl")
    ELASTICSEARCH_DSL = {"default": {"hosts": ES_URL}}

AUTHENTICATION_BACKENDS = [
    "saleor.account.backends.facebook.CustomFacebookOAuth2",
    "saleor.account.backends.google.CustomGoogleOAuth2",
    # "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]


# GRAPHQL_JWT = {"JWT_PAYLOAD_HANDLER": "saleor.graphql.utils.create_jwt_payload"}

SOCIAL_AUTH_PIPELINE = [
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
]

SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_USER_MODEL = AUTH_USER_MODEL
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email"]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {"fields": "id, email"}
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True


CELERY_BROKER_URL = (
    os.environ.get("CELERY_BROKER_URL", os.environ.get("CLOUDAMQP_URL")) or ""
)
CELERY_TASK_ALWAYS_EAGER = not CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", None)

# Impersonate module settings
IMPERSONATE = {
    "URI_EXCLUSIONS": [r"^dashboard/"],
    "CUSTOM_USER_QUERYSET": "saleor.account.impersonate.get_impersonatable_users",  # noqa
    "USE_HTTP_REFERER": True,
    "CUSTOM_ALLOW": "saleor.account.impersonate.can_impersonate",
}


# Rich-text editor
ALLOWED_TAGS = [
    "a",
    "b",
    "blockquote",
    "br",
    "em",
    "h2",
    "h3",
    "i",
    "img",
    "li",
    "ol",
    "p",
    "strong",
    "ul",
]
ALLOWED_ATTRIBUTES = {"*": ["align", "style"], "a": ["href", "title"], "img": ["src"]}
ALLOWED_STYLES = ["text-align"]


# Slugs for menus precreated in Django migrations
DEFAULT_MENUS = {"top_menu_name": "navbar", "bottom_menu_name": "footer"}

# This enable the new 'No Captcha reCaptcha' version (the simple checkbox)
# instead of the old (deprecated) one. For more information see:
#   https://github.com/praekelt/django-recaptcha/blob/34af16ba1e/README.rst
NOCAPTCHA = True

# Set Google's reCaptcha keys
RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")


##  Sentry
# SENTRY_DSN = os.environ.get("SENTRY_DSN")
# if SENTRY_DSN:
#    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()])

GRAPHENE = {
    "RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST": True,
    "RELAY_CONNECTION_MAX_LIMIT": 100,
}

EXTENSIONS_MANAGER = "saleor.extensions.manager.ExtensionsManager"

PLUGINS = [
    "saleor.extensions.plugins.avatax.plugin.AvataxPlugin",
    "saleor.extensions.plugins.vatlayer.plugin.VatlayerPlugin",
    "saleor.extensions.plugins.webhook.plugin.WebhookPlugin",
    "saleor.payment.gateways.dummy.plugin.DummyGatewayPlugin",
    "saleor.payment.gateways.stripe.plugin.StripeGatewayPlugin",
    "saleor.payment.gateways.braintree.plugin.BraintreeGatewayPlugin",
    "saleor.payment.gateways.razorpay.plugin.RazorpayGatewayPlugin",
]

# Whether DraftJS should be used be used instead of HTML
# True to use DraftJS (JSON based), for the 2.0 dashboard
# False to use the old editor from dashboard 1.0
USE_JSON_CONTENT = get_bool_from_env("USE_JSON_CONTENT", False)

# SCH++
DATA_UPLOAD_MAX_MEMORY_SIZE = 32000000
SESSION_COOKIE_AGE = 28800
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SHOP_URL = "https://sklep.polbruk.pl"

SHOP_EMAIL_SUBJECT = "Polbruk SA - sklep internetowy zaprasza!"
SHOP_EMAIL_FROM = "sklep@polbruk.pl"


ENABLE_SILK = False

IN_FRAME = True
# SCH--
from pytigon_lib.schtools.install_init import init

init(PRJ_NAME, ROOT_PATH, DATA_PATH, PRJ_PATH, STATIC_ROOT, [MEDIA_ROOT, UPLOAD_PATH])

START_PAGE = "shop/test/?fragment=page"
SHOW_LOGIN_WIN = True
PACKS = []

for app in APPS:
    if "." in app:
        pack = app.split(".")[0]
        if pack not in PACKS:
            PACKS.append(pack)
            p1 = os.path.join(LOCAL_ROOT_PATH, pack)
            if p1 not in sys.path:
                sys.path.append(p1)
            p2 = os.path.join(PRJ_PATH_ALT, pack)
            if p2 not in sys.path:
                sys.path.append(p2)

    if app not in [x if isinstance(x, str) else x.label for x in INSTALLED_APPS]:
        a = get_app_config(app)
        if app not in INSTALLED_APPS:
            INSTALLED_APPS.append(get_app_config(app))
        aa = app.split(".")
        for root_path in [PRJ_PATH, PRJ_PATH_ALT]:
            base_path = os.path.join(root_path, aa[0])
            if os.path.exists(base_path):
                TEMPLATES[0]["DIRS"].append(os.path.join(base_path, "templates"))
                if len(aa) == 2:
                    if base_path not in sys.path:
                        sys.path.append(base_path)
                    locale_path = os.path.join(base_path, "locale")
                    if locale_path not in LOCALE_PATHS:
                        if os.path.exists(locale_path):
                            LOCALE_PATHS.append(os.path.join(base_path, "locale"))

for app in APPS_EXT:
    if app not in INSTALLED_APPS:
        INSTALLED_APPS.append(app)

if os.path.exists(PRJ_PATH + "/_schcomponents/static"):
    STATICFILES_DIRS.append(PRJ_PATH + "/_schcomponents/static")
else:
    STATICFILES_DIRS.append(PRJ_PATH_ALT + "/_schcomponents/static")


TEMPLATES[0]["DIRS"].insert(0, os.path.join(DATA_PATH, PRJ_NAME, "templates"))
TEMPLATES[0]["DIRS"].insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
)
TEMPLATES[0]["DIRS"].insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")
)
LOCALE_PATHS.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "locale"))

_NAME = os.path.join(
    DATA_PATH, f"{URL_ROOT_FOLDER if URL_ROOT_FOLDER else PRJ_NAME}/{PRJ_NAME}.db"
)

DATABASES["default"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": _NAME,
}

if setup_databases:
    db_setup = setup_databases(PRJ_NAME)
    db_local = DATABASES["default"]
    for key, value in db_setup[0].items():
        DATABASES[key] = value
    DATABASES["local"] = db_local
    if db_setup[1]:
        AUTHENTICATION_BACKENDS = db_setup[1]
else:
    if PRJ_NAME.upper() + "_DATABASE_URL" in os.environ:
        db_local = DATABASES["default"]
        DATABASES["default"] = ENV.db(
            var=os.environ[PRJ_NAME.upper() + "_DATABASE_URL"]
        )
        DATABASES["local"] = db_local
    elif "DATABASE_URL" in os.environ:
        db_local = DATABASES["default"]
        DATABASES["default"] = ENV.db()
        DATABASES["local"] = db_local
    else:
        DATABASES["local"] = {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": _NAME.replace(".db", "_local.db"),
        }


try:
    from settings_app_local import *
except ImportError:
    pass

GEN_TIME = "2026-07-06 18:52:23"


for key, value in os.environ.items():
    if key.startswith("PYTIGON_") or key.startswith(
        "PYTIGON" + (URL_ROOT_FOLDER if URL_ROOT_FOLDER else PRJ_NAME).upper() + "_"
    ):
        key2 = key.split("_", 1)[1]
        if value.startswith("[") or value.startswith("{") or value.startswith(":"):
            try:
                globals()[key2] = json.loads(
                    value[1 if value.startswith(":") else 0 :]
                    .replace("'", '"')
                    .replace("[|]", "!")
                    .replace('["]', '\\"')
                )
            except json.JSONDecodeError:
                print(f"invalid json syntax for environment variable: {key}")
        else:
            globals()[key2] = value


finish(globals())
