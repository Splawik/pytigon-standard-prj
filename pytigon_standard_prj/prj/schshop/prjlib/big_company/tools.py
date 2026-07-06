from saleor.product import models as product_models
from saleor.checkout import models as checkout_models
from django.db import models
from big_company.models import get_request, get_profile, get_profile_id, PriceDoc
from prices import Money
from decimal import Decimal

from django.db.models import Avg, Max, Min, Sum, Count, Q
from django.conf import settings
from django.core.validators import MinValueValidator

from saleor.core.models import PublishedQuerySet
from django_prices.models import MoneyField
import types

from django.db.models.manager import Manager

def base_price(self):
    request = get_request()    
    if request:
        if hasattr(request, "user") and request.user.is_authenticated:        
            if request.user.is_superuser:
                if self.converter and self.converter != 1:
                    return self.product.price * Decimal(self.converter)
                else:
                    return self.product.price
            else:  
                p = get_profile()
                if p:
                    tab = request.session.get('ph_list', None)
                    if not tab:
                        tab = {}
                        ph_list  = PriceDoc.objects.filter(platnik=p['platnik'], budowa=p['budowa'], mag=p['magazyn'])
                        for ph in ph_list:                            
                            tab[ph.group] = ph.cena
                        request.session['ph_list'] = tab
                    if self.converter and self.converter != 1:
                        if self.product.seo_title in tab:
                            return Money(Decimal(tab[self.product.seo_title]) * Decimal(self.converter),"PLN")                            
                        if self.product.group in tab:
                            return Money(Decimal(tab[self.product.group]) * Decimal(self.converter) ,"PLN")
                    else:
                        if self.product.seo_title in tab:
                            return Money(Decimal(tab[self.product.seo_title]),"PLN")
                        if self.product.group in tab:
                            return Money(Decimal(tab[self.product.group]),"PLN")
    
    if self.converter and self.converter != 1:
        return self.product.price * Decimal(self.converter)
    else:
        return self.product.price

