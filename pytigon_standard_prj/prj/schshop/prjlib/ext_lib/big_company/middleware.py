import logging
import random
import re

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import MiddlewareNotUsed
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from django.utils.translation import get_language, ugettext_lazy as _
from django_countries.fields import Country

from big_company.models import get_profile

logger = logging.getLogger(__name__)


def profile(get_response):

    def middleware(request):
        if request.session:
            if request and hasattr(request, "user") and request.user.is_authenticated and not request.session.get('profile', None):             
                get_profile(request)
        return get_response(request)

    return middleware
