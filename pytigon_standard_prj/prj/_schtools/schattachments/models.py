from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pytigon_lib.schdjangoext.fields import *
import pytigon_lib.schdjangoext.fields as ext_models
from pytigon_lib.schdjangoext.models import *

import schelements.models


def upload_path_fun(obj, filename):
    return (
        "doc/attachments/"
        + obj.application
        + "_"
        + obj.table
        + "_"
        + str(obj.parent_id)
        + "_"
        + obj.group
        + "_"
        + filename
    )


class Attachment(AssociatedJSONModel):
    class Meta:
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schattachments"

        ordering = ["id"]

        permissions = [
            ("admin_attachment", "Can administer attachments"),
        ]

    name = models.CharField(
        "Name", null=True, blank=True, editable=True, max_length=256
    )
    ext = models.CharField(
        "Extension", null=True, blank=True, editable=False, max_length=64
    )
    thumb = models.TextField(
        "thumbnail",
        null=True,
        blank=True,
        editable=False,
    )
    upload_date = models.DateTimeField(
        "Upload date",
        null=False,
        blank=False,
        editable=False,
        default=timezone.now,
    )
    modify_date = models.DateTimeField(
        "Modify date",
        null=True,
        blank=True,
        editable=False,
        default=timezone.now,
    )
    file = models.FileField(
        "Select file", null=False, blank=False, editable=True, upload_to=upload_path_fun
    )
    folder = ext_models.PtigForeignKey(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        editable=True,
        verbose_name="Folder",
        db_index=True,
        search_fields=[
            "name__icontains",
        ],
        limit_choices_to={"type__startswith": "C-FLD"},
    )
    description = models.CharField(
        "Description", null=True, blank=True, editable=True, max_length=256
    )
    status = models.CharField(
        "Status", null=True, blank=True, editable=True, max_length=16
    )

    def save(self, *args, **kwargs):
        self.ext = self.file.url.split(".")[-1].upper()
        if not self.name:
            self.name = str(self.file)
        super(Attachment, self).save(*args, **kwargs)

    def is_image(self):
        if self.ext.lower() in ("png", "jpg", "jpeg", "svg"):
            return True
        else:
            return False


admin_register(Attachment)
