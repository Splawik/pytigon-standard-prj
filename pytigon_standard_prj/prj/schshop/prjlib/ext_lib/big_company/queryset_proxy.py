from saleor.product import models as product_models
from saleor.checkout import models as checkout_models
from django.db import models
from big_company.models import get_request, get_profile, get_profile_id, PriceDoc
from prices import Money
from decimal import Decimal

from django.db.models import Avg, Max, Min, Sum, Count, Q, F
from django.conf import settings
from django.core.validators import MinValueValidator

from saleor.core.models import PublishedQuerySet
from django_prices.models import MoneyField
import types

from django.db.models.manager import Manager


class Proxy():
    def __init__(self, obj):
        self.____obj____ = obj
       
    def __getattr__(self, attr):
        if attr.startswith('____'):
            return super().__getattr__(attr)
        else:
            return getattr(self.____obj____,attr)

    def __setattr__(self, attr, value):
        if attr.startswith('____'):
            return super().__setattr__(attr, value)
        else:
            return setattr(self.____obj___, attr, value)


class QuerySetProxy(Proxy):
    def all(self, *argi, **argv):
        q = self.____obj____.all(*argi, **argv)
        return self.default_filter(q)

    def filter(self, *argi, **argv):
        q = self.____obj____.filter(*argi, **argv)
        return self.default_filter(q)

    def published(self, *argi, **argv):
        q = self.____obj____.published(*argi, **argv)
        return self.default_filter(q)

    def for_display(self, *argi, **argv):
        q = self.____obj____.for_display(*argi, **argv)
        return self.default_filter(q)

    def default_filter(self, q):
        return q


class ProductProxy(QuerySetProxy):
    def default_filter(self, q):
        p = get_profile()
        if p:
            variants_count = Count('variants', filter=Q(variants__quantity__gt = F('variants__quantity_allocated'), variants__param1 = p['magazyn'])|Q(variants__sku='paleta'))             
            return q.annotate(vc=variants_count).filter(vc__gt=0)            
        return q            

product_models.Product.objects = ProductProxy(product_models.Product.objects)


class ProductVariantProxy(QuerySetProxy):
    def default_filter(self, q):
        p = get_profile()
        if p:
            return q.filter(Q(quantity__gt = 0, param1 = p['magazyn'])|Q(sku='paleta'))
        return q

product_models.ProductVariant.objects = ProductVariantProxy(product_models.ProductVariant.objects)


class CheckoutProxy(QuerySetProxy):
    def default_filter(self, q):
        pid = get_profile_id()
        if pid:
            q =  q.filter(profile_str = pid) 
            return q
        return q

checkout_models.Checkout.objects = CheckoutProxy(checkout_models.Checkout.objects)


