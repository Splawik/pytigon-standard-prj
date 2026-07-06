from decimal import Decimal
from operator import attrgetter
from uuid import uuid4

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Max, Sum
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from django_prices.models import MoneyField, TaxedMoneyField
from prices import Money, TaxedMoney

from saleor.product.models import Category, Product, ProductType,  Attribute, AttributeValue, ProductVariant, Collection, AssignedProductAttribute
from saleor.account.models import User
from big_company.models import CustomerProfile, PriceDoc

