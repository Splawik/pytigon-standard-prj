from django.db import models
from django.utils.translation import gettext_lazy as _

from pytigon_lib.schdjangoext.fields import *
from pytigon_lib.schdjangoext.models import *


class Rights(models.Model):
    class Meta:
        verbose_name = _("Rights")
        verbose_name_plural = _("Rights")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schodfupload"

        ordering = ["id"]

    title = models.CharField(
        "Title", null=True, blank=True, editable=True, max_length=64
    )


admin_register(Rights)
