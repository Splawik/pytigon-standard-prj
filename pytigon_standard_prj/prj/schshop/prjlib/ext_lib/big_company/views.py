import datetime
import json

from django.http import HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.http import Http404, HttpResponseForbidden, HttpResponse

from .models import filter_profiles, set_profile as set_profile2

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
    logout as auth_logout, update_session_auth_hash,
)

from django.urls import reverse, reverse_lazy
from django.contrib.auth import views as django_views
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
import django

from saleor.core.utils import build_absolute_uri


def find_profile(request):
    q = request.GET.get('q', None)    
    objs = filter_profiles(q)
    ret = []
    if objs:
        ukryj_budowy = request.session['profile']['profile_short']        
        for obj in objs:
            o = {}
            o['id'] = obj. profileid
            if ukryj_budowy:
                o['text'] = obj.magazyn_name
            else:
                o['text'] = obj.magazyn_name + " / " + obj.budowa_name 
            ret.append(o)
    
    return JsonResponse({'results': ret})

@csrf_exempt
def set_profile(request):
    profileid = request.POST.get('profileid', None) 
    if profileid and set_profile2(profileid):
        return HttpResponse("OK")
    else:
        return HttpResponse("Error")


def invite(request, uid):
    UserModel = get_user_model()
    user = UserModel.objects.get(pk=uid)
    
    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain
    user_email = user.email
    
    reset_url = build_absolute_uri(
        reverse(
            "account:reset-password-confirm",
            kwargs={"uidb64": urlsafe_base64_encode(force_bytes(user.pk)), "token": default_token_generator.make_token(user)},
        )
    )
    reset_url = reset_url.replace('http://', 'https://')
    context = {
        'email': user_email,
        'domain': domain,
        'site_name': site_name,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'user': user,
        'token': default_token_generator.make_token(user),                
        'reset_url': reset_url,
    }
    subject = settings.SHOP_EMAIL_SUBJECT
    body = loader.render_to_string('templated_email/compiled/welcome.html', context)

    email_message = EmailMultiAlternatives(subject, body, settings.SHOP_EMAIL_FROM, [user_email])        
    
    html_email = loader.render_to_string('templated_email/compiled/welcome.html', context)
    email_message.attach_alternative(html_email, 'text/html')

    email_message.send()

    return HttpResponse("OK: " + str(uid))
