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


class Information(models.Model):

    class Meta:
        verbose_name = _("Information")
        verbose_name_plural = _("Information")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "information"

        ordering = ["id"]

    description = models.CharField(
        "Description", null=True, blank=True, editable=True, max_length=256
    )


admin_register(Information)
