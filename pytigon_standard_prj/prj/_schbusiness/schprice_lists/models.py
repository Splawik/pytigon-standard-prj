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


class RetailPrice(models.Model):

    class Meta:
        verbose_name = _("Retail price")
        verbose_name_plural = _("Retail price list")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schprice_lists"

        ordering = ["id"]

    sold_item = ext_models.PtigForeignKey(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Sold item",
        db_index=True,
        related_name="sold_item_retail_prices",
    )
    retail_price = models.DecimalField(
        "Retail price",
        null=False,
        blank=False,
        editable=True,
        decimal_places=2,
        max_digits=12,
    )


admin_register(RetailPrice)


class Price(models.Model):

    class Meta:
        verbose_name = _("Price")
        verbose_name_plural = _("Price list")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schprice_lists"

        ordering = ["id"]

    sold_item = ext_models.PtigForeignKey(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Sold item",
        db_index=True,
        related_name="sold_item_prices",
    )
    consumer = ext_models.PtigForeignKey(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        editable=True,
        verbose_name="Consumer",
        db_index=True,
        related_name="customer_prices",
    )
    retail_price = models.DecimalField(
        "Retail price",
        null=False,
        blank=False,
        editable=True,
        decimal_places=2,
        max_digits=12,
    )
    price = models.DecimalField(
        "price", null=False, blank=False, editable=True, decimal_places=2, max_digits=12
    )
    discount_in_words = models.CharField(
        "Discount in words", null=True, blank=True, editable=True, max_length=1024
    )


admin_register(Price)
