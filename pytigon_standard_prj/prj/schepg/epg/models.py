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


import datetime

ElementChoices = [
    ("c", "channel"),
    ("g", "category"),
]


class Epg(models.Model):

    class Meta:
        verbose_name = _("Epg")
        verbose_name_plural = _("Epg")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "epg"

        ordering = ["id"]

    channel = models.CharField(
        "Channel", null=False, blank=False, editable=True, max_length=64
    )
    date_from = models.DateTimeField(
        "Date from",
        null=False,
        blank=False,
        editable=True,
    )
    date_to = models.DateTimeField(
        "Date to",
        null=False,
        blank=False,
        editable=True,
    )
    title = models.CharField(
        "Title", null=False, blank=False, editable=True, max_length=256
    )
    description = models.TextField(
        "Description",
        null=True,
        blank=True,
        editable=False,
    )
    rating = models.IntegerField(
        "Rating",
        null=True,
        blank=True,
        editable=True,
    )
    category = models.CharField(
        "Category", null=True, blank=True, editable=True, max_length=64
    )
    country = models.CharField(
        "Country", null=True, blank=True, editable=True, max_length=64
    )
    year = models.IntegerField(
        "Year",
        null=True,
        blank=True,
        editable=True,
    )

    @staticmethod
    def sort(queryset, sort_parm, order_parm):
        return queryset.order_by("date_from")

    def started(self):
        if self.date_from <= timezone.now():
            return True
        else:
            return False


admin_register(Epg)


class BlockEpg(models.Model):

    class Meta:
        verbose_name = _("Block epg category")
        verbose_name_plural = _("Block epg category")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "epg"

        ordering = ["id"]

    element = models.CharField(
        "Element",
        null=False,
        blank=False,
        editable=True,
        choices=ElementChoices,
        max_length=1,
    )
    pattern = models.CharField(
        "Pattern", null=True, blank=True, editable=True, max_length=256
    )


admin_register(BlockEpg)
