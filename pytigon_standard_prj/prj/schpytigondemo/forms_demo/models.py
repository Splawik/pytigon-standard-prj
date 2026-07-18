from django.db import models
from django.utils.translation import gettext_lazy as _

from pytigon_lib.schdjangoext.fields import *
from pytigon_lib.schdjangoext.models import *


test_choice = [
    ("1", "Test 1"),
    ("2", "Test 2"),
    ("3", "Test 3"),
    ("4", "Test 4"),
    ("5", "Test 5"),
    ("6", "Test 6"),
    ("7", "Test 7"),
    ("8", "Test 8"),
]


class Select2Example(models.Model):
    """
    Simple lookup model providing name entries for Select2 form fields.

    Used as a ForeignKey/ManyToManyField source in form_test3 to
    demonstrate the Select2 autocomplete widget integration.
    """

    class Meta:
        verbose_name = _("Select2 example")
        verbose_name_plural = _("Select2 examples")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "forms_demo"

        ordering = ["id"]

    name = models.CharField(
        "Name", null=False, blank=False, editable=True, max_length=64
    )

    def __str__(self):
        return self.name


admin_register(Select2Example)
