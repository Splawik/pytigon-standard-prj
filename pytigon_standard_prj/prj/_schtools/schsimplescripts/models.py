from django.db import models
from django.utils.translation import gettext_lazy as _
from pytigon_lib.schdjangoext.fields import *
from pytigon_lib.schdjangoext.models import *
from schsimplescripts.script_tools import decode_script

VIEW = """#Example: 
#import datetime
#
#def view(request, data):
#    pass
    
"""


class Script(models.Model):
    class Meta:
        verbose_name = _("Script")
        verbose_name_plural = _("Scripts")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schsimplescripts"

        ordering = ["id"]

        permissions = [
            ("admin_script", "Can administer scripts"),
        ]

    name = models.CharField(
        _("Name"), null=False, blank=False, editable=True, db_index=True, max_length=64
    )
    title = models.CharField(
        _("Title"), null=True, blank=True, editable=True, max_length=64
    )
    code = models.TextField(
        _("Code"),
        null=True,
        blank=True,
        editable=False,
    )
    category = models.CharField(
        _("Category"),
        null=True,
        blank=True,
        editable=True,
        db_index=True,
        max_length=64,
    )
    rights_group = models.CharField(
        _("Rights group"), null=True, blank=True, editable=True, max_length=64
    )
    menu = models.CharField(
        _("Menu"), null=True, blank=True, editable=True, max_length=64
    )
    doc = models.TextField(
        _("Doc"),
        null=True,
        blank=True,
        editable=False,
    )
    _form = models.TextField(
        _("_form"),
        null=True,
        blank=True,
        editable=True,
    )
    _view = models.TextField(
        _("_view"),
        null=True,
        blank=True,
        editable=True,
    )
    _template = models.TextField(
        _("_template"),
        null=True,
        blank=True,
        editable=True,
    )

    def save(self, *args, **kwargs):
        code = self.code
        if code:
            x = decode_script(self.name, code)
            if x:
                self._form = x[0]
                self._view = x[1]
                self._template = x[2]
            else:
                code = ""

        if not code:
            self._form = ""
            self._view = ""
            self._template = ""

        super().save(*args, **kwargs)

    def get__view_if_empty(self, request, template_name, ext, extra_context, target):
        return VIEW


admin_register(Script)
