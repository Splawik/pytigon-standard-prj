from django.db import models
from django.utils.translation import gettext_lazy as _

from pytigon_lib.schdjangoext.fields import *
from pytigon_lib.schdjangoext.models import *


class SChSetup(models.Model):
    class Meta:
        verbose_name = _("SChSetup")
        verbose_name_plural = _("SChSetups")
        default_permissions = ("can_administer", "add", "change", "delete", "list")
        app_label = "schadmin"

    # name = models.CharField(
    #    "Name", null=False, blank=False, editable=True, max_length=255
    # )


# content_type = ContentType.objects.get_for_model(SChSetup)

# permission = Permission.objects.create(
#    codename='can_administer',
#    name='Can administer',
#    content_type = content_type
# )
