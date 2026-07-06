import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import HStoreField
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.text import slugify
from django.utils.translation import pgettext_lazy
from django_prices.models import MoneyField
from django_prices.templatetags import prices_i18n
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from prices import TaxedMoneyRange
from text_unidecode import unidecode
from versatileimagefield.fields import PPOIField, VersatileImageField

from saleor.core.exceptions import InsufficientStock
from saleor.core.models import SortableModel
try:
    from saleor.plugins.vatlayer import DEFAULT_TAX_RATE_NAME, apply_tax_to_price
except:
    from saleor.extensions.plugins.vatlayer import DEFAULT_TAX_RATE_NAME, apply_tax_to_price

from saleor.discount.utils import calculate_discounted_price
from saleor.seo.models import SeoModel

#SCH++
from django.db.models import Avg, Count
from prices import Money
import json
from django.db.models import Avg, Max, Min, Sum
from django.forms.models import model_to_dict
import logging
import inspect

def get_request():
    frame = None
    r = None
    try:
        for f in inspect.stack()[1:]:
            frame = f[0]
            code = frame.f_code

            if code.co_varnames[:1] == ("request",):
                try:
                    r = frame.f_locals["request"]
                except:
                    r = None
            elif code.co_varnames[:2] == ("self", "request",):
                try: 
                    r = frame.f_locals["request"]
                except:
                    r = None
            if r and hasattr(r, 'session'):
                return r
            else:
                r = None
    finally:
        if frame:
            del frame
    return None

class CustomerProfile(models.Model):
    email = models.CharField(max_length=128)    
    profileid = models.CharField(max_length=128)    
    platnik = models.CharField(max_length=16)
    budowa = models.CharField(max_length=16)
    magazyn = models.CharField(max_length=16)

    platnik_name = models.CharField(max_length=128)    
    budowa_name = models.CharField(max_length=128)    
    magazyn_name = models.CharField(max_length=128)    
    
    def __str__(self):
        return self.profileid


def check_profiles(profiles):
    ukryj_budowy=True
    old_budowa = None    
    for obj in profiles:
        if old_budowa and obj.budowa != old_budowa:
            ukryj_budowy = False
            break
        old_budowa = obj.budowa    
    return ukryj_budowy


def get_profile(req=None):
    if req:
        request = req
    else:
        request = get_request()
    if request and hasattr(request, "user") and request.user.is_authenticated: 
        profile = request.session.get('profile', None)
        if profile:
            return profile
        else:
            profiles = CustomerProfile.objects.filter(email = request.user.email)
            if profiles.count() > 0:
                if set_profile(profiles[0].profileid):
                    return get_profile()
    return None

def get_profile_id():
    request = get_request()
    p = get_profile()
    if p:
        return p['profileid']
    return None

def set_profile(profileid):
    request = get_request()
    if request and hasattr(request, "user") and request.user.is_authenticated: 
        profiles = CustomerProfile.objects.filter(profileid = profileid)        
        profiles2 = CustomerProfile.objects.filter(email = request.user.email)
        if profiles.count()>0:
            profile = profiles[0]            
            p = model_to_dict(profiles[0])
            short = check_profiles(profiles2)
            if short:
                p['profile_str'] = profile.magazyn_name
            else:
                p['profile_str'] =  profile.magazyn_name + " / " + profile.budowa_name
            p['profile_count'] = len(profiles2)
            p['profile_short'] = short
            request.session['profile'] = p
            return True
    return False


def filter_profiles(s):
    request = get_request()
    if request and hasattr(request, "user") and request.user.is_authenticated: 
        if s:
            words = s.split(' ')
            q = []
            for word in words:
                tmp  = Q(budowa_name__icontains = word)  | Q(budowa = word) | Q(magazyn_name__icontains = word) | Q(magazyn = word)
                q.append(tmp)
            profiles = CustomerProfile.objects.filter(email = request.user.email)
            for pos in q:                
                profiles = profiles.filter(pos)
        else:
            profiles = CustomerProfile.objects.filter(email = request.user.email)
        if 'profile' in request.session:                
            x = request.session['profile']
            ret = []                
            for profile in profiles:
                if profile.profileid == x['profileid']:
                    ret.insert(0,profile)
                else:
                    ret.append(profile)
            profiles = ret
        return profiles
    return []
    
    
    
class PriceDoc(models.Model):
    
    doc_name = models.CharField(max_length=128)    
    platnik = models.CharField(max_length=16)
    budowa = models.CharField(max_length=16)
    mag = models.CharField(max_length=16)
    
    symkar = models.CharField(max_length=16, null=True, blank=True)
    group = models.CharField(max_length=16)

    koszt_tr = models.FloatField()    
    cena = models.FloatField()    
   
    def __str__(self):
        return self.doc_name + "/" + self.group


class UserData(models.Model):
    typ = models.CharField(max_length=16)
    row_id = models.IntegerField()    
    platnik = models.CharField(max_length=16)
    budowa = models.CharField(max_length=16)
    magazyn = models.CharField(max_length=16)
    json_row = models.TextField()
    
    def get_row(self):
        if self.json_row:            
            return json.loads(self.json_row)
        else:
            return None

class Accept(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=256, null=True, blank=True)
    value = models.CharField(max_length=256, null=True, blank=True)
