from django.db import models
from django.utils.translation import gettext_lazy as _

from pytigon_lib.schdjangoext.fields import *
from pytigon_lib.schdjangoext.models import *


class Teest(models.Model):
    class Meta:
        verbose_name = _("Test")
        verbose_name_plural = _("Tests")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "db_demo"

        ordering = ["id"]

    description = models.CharField(
        "Description", null=False, blank=False, editable=True, max_length=256
    )


admin_register(Teest)
