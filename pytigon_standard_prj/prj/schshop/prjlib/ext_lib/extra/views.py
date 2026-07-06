import datetime
import json

from django.http import HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.http import Http404, HttpResponseForbidden, HttpResponse

from .models import Accept

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

@csrf_exempt
def extra_accept(request, key, value):
    obj = Accept()
    obj.key = key
    obj.value = value
    obj.save()
    context = { 'obj': obj, }
    return render(request, "extra/accept.html", context)
    