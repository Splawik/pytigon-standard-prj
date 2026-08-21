import pytigon_lib.schdjangoext.fields as ext_models
from django.db import models
from django.utils.translation import gettext_lazy as _
from pytigon_lib.schdjangoext.fields import *
from pytigon_lib.schdjangoext.models import *


class bookmarks(models.Model):
    class Meta:
        verbose_name = _("Bookmarks")
        verbose_name_plural = _("Bookmarks")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schbrowser"

        ordering = ["id"]

    parent = ext_models.PtigHiddenForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        editable=True,
        verbose_name=_("Parent"),
    )
    name = models.CharField(
        _("Name"), null=False, blank=False, editable=True, max_length=64
    )
    url = models.CharField(
        _("url"), null=True, blank=True, editable=True, max_length=256
    )


admin_register(bookmarks)


class history(models.Model):
    class Meta:
        verbose_name = _("History")
        verbose_name_plural = _("History")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schbrowser"

        ordering = ["id"]

    date = models.DateTimeField(
        _("Date"), null=True, blank=True, editable=True, auto_now=True
    )
    url = models.CharField(
        _("url"), null=False, blank=False, editable=True, max_length=256
    )


admin_register(history)
