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

StartEffect = [
    ("1", "show"),
    ("2", "appearance"),
    ("3", "show from the left"),
    ("4", "show from the right"),
    ("5", "show from the top"),
    ("6", "show from the bottom"),
    ("7", "show from the faraway"),
    ("8", "chessboard"),
    ("9", "sales"),
    ("a", "flashing"),
]

EndEffect = [
    ("1", "hide"),
    ("2", "disappearance"),
    ("3", "hide to the right"),
    ("4", "hide to the left"),
    ("5", "hide to the bottom"),
    ("6", "hide to the top"),
    ("7", "hide to the faraway"),
]

Style = [
    ("1", "primary"),
    ("2", "secondary"),
    ("3", "success"),
    ("4", "danger"),
    ("5", "warning"),
    ("6", "info"),
    ("7", "light alert"),
    ("8", "dark alert"),
]

Position = [
    ("fs", "FullScreen"),
    ("top", "Top"),
    ("top-left", "Top left"),
    ("top-right", "Top right"),
    ("bottom", "Bottom"),
    ("bottom-left", "Bottom left"),
    ("bottom-right", "Bottom right"),
    ("1_4", "first quarter"),
    ("2_4", "second quarter"),
    ("3_4", "third quarter"),
    ("4_4", "fourth quarter"),
]


class Show(models.Model):

    class Meta:
        verbose_name = _("Show")
        verbose_name_plural = _("Shows")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schslides"

        ordering = ["id"]

    name = models.CharField(
        "Name", null=False, blank=False, editable=True, max_length=64
    )


admin_register(Show)


class Slide(models.Model):

    class Meta:
        verbose_name = _("Slide")
        verbose_name_plural = _("Slides")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schslides"

        ordering = ["id"]

    parent = ext_models.PtigForeignKey(
        Show,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Parent",
    )
    description = models.CharField(
        "Description", null=True, blank=True, editable=True, max_length=64
    )
    time = models.FloatField(
        "Time",
        null=True,
        blank=True,
        editable=True,
    )
    start_effect = models.CharField(
        "Start effect",
        null=True,
        blank=True,
        editable=True,
        choices=StartEffect,
        max_length=16,
    )
    start_effect_param = models.CharField(
        "Start effect parameters", null=True, blank=True, editable=True, max_length=32
    )
    end_effect = models.CharField(
        "End effect",
        null=True,
        blank=True,
        editable=True,
        choices=EndEffect,
        max_length=16,
    )
    end_effect_param = models.CharField(
        "End effect parameters", null=True, blank=True, editable=True, max_length=32
    )
    end_effect_shift = models.IntegerField(
        "End effect shift",
        null=True,
        blank=True,
        editable=True,
    )
    file = models.FileField(
        "File", null=True, blank=True, editable=True, upload_to="upload/"
    )
    style = models.CharField(
        "Style", null=True, blank=True, editable=True, choices=Style, max_length=16
    )
    position = models.CharField(
        "Position",
        null=True,
        blank=True,
        editable=True,
        choices=Position,
        max_length=16,
    )
    z_index = models.IntegerField(
        "Z index",
        null=True,
        blank=True,
        editable=True,
    )


admin_register(Slide)
