import os, os.path
import sys

import django
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import admin

from pytigon_lib.schdjangoext.fields import *
import pytigon_lib.schdjangoext.fields as ext_models
from pytigon_lib.schdjangoext.models import *
from pytigon_lib.schtools import schjson
from pytigon_lib.schhtml.htmltools import superstrip

import schelements.models
import schprofile.models


from decimal import Decimal
from payments import PurchasedItem
from payments.models import BasePayment

from collections.abc import Iterable
from django.db.models import Q, Sum
from django.conf import settings


class ShopGood(schelements.models.Element):

    class Meta:
        verbose_name = _("Shop good")
        verbose_name_plural = _("Shop goods")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schshop"

        ordering = ["id"]

        proxy = True

    @staticmethod
    def filter_by_permissions(view, queryset_or_obj, request):
        if False:
            q = None
            doc_regs = None

            if hasattr(request, "user") and request.user.is_superuser:
                return queryset_or_obj

            if hasattr(request, "user") and hasattr(request.user, "profile"):
                profile = request.user.profile
                if profile.doc_regs:
                    doc_regs = list(
                        [
                            item.strip()
                            for item in profile.doc_regs.replace(",", ";").split(";")
                            if item.strip()
                        ]
                    )
            else:
                profile = None

        queryset = queryset_or_obj.filter(
            Q(type__startswith="I-PRD") | Q(type__startswith="I-MER")
        ).filter(
            accountstate__parent__name="@-qty",
            accountstate__aggregate=False,
            accountstate__zero_balance=False,
        )
        if hasattr(settings, "INTERNET_SALE_LABEL") and settings.INTERNET_SALE_LABEL:
            queryset = queryset.filter(
                elementlabel__type__name=settings.INTERNET_SALE_LABEL
            )
        queryset = (
            queryset.annotate(
                quantity=Sum("accountstate__credit") - Sum("accountstate__debit")
            )
            .filter(sold_item_retail_prices__retail_price__gt=0)
            .annotate(
                price=Sum("sold_item_prices__price"),
                retail_price=Sum("sold_item_retail_prices__retail_price"),
            )
        )
        return queryset


admin_register(ShopGood)


class ShoppingCart(JSONModel):

    class Meta:
        verbose_name = _("Shopping cart")
        verbose_name_plural = _("Shopping cart")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schshop"

        ordering = ["id"]

    product = ext_models.PtigForeignKey(
        ShopGood,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Product",
        related_name="shoppingcart_product_set",
    )
    qty = models.IntegerField(
        "Quantity",
        null=False,
        blank=False,
        editable=True,
        default=1,
    )
    user = ext_models.PtigForeignKey(
        schprofile.models.UserProxy,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="User",
    )
    customer = ext_models.PtigForeignKey(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        editable=True,
        verbose_name="Customer",
        limit_choices_to={"type__startswith": "O-CUS"},
        related_name="shoppingcart_customer_set",
    )


admin_register(ShoppingCart)


class ProxyPayment(BasePayment):

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Paymants")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schshop"

        ordering = ["id"]

        abstract = True


class Payment(ProxyPayment):

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schshop"

        ordering = ["id"]

    parent = ext_models.PtigForeignKey(
        schelements.models.DocHead,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Parent",
    )

    def get_failure_url(self) -> str:
        return f"http://127.0.0.1:8000/schshop/payment_info/{self.pk}/failure/"

    def get_success_url(self) -> str:
        return f"http://127.0.0.1:8000/schshop/payment_info/{self.pk}/success/"

    def get_purchased_items(self) -> Iterable[PurchasedItem]:
        yield PurchasedItem(
            name="The Hound of the Baskervilles",
            sku="BSKV",
            quantity=9,
            price=Decimal(10),
            currency="PLN",
        )

    @classmethod
    def filter(cls, value, view=None, request=None):
        if value:
            return cls.objects.filter(parent_id=int(value))
        else:
            return cls.objects.all()

    def get_form(self, *argi, **argv):
        print("F1:", len(argi))
        if len(argi) == 4:
            return None
        else:
            return super().get_form(*argi, **argv)


admin_register(Payment)
