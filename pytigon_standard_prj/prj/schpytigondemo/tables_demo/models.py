from django.db import models
from django.utils.translation import gettext_lazy as _

from pytigon_lib.schdjangoext.fields import *
import pytigon_lib.schdjangoext.fields as ext_models
from pytigon_lib.schdjangoext.models import *


from django.db.models.signals import post_save
from django.dispatch import receiver
from schattachments.models import Attachment
from pytigon_lib.schdjangoext.tools import from_migrations

if not from_migrations():

    @receiver(post_save, sender=Attachment)
    def attachment_created(sender, instance, created, **kwargs):
        if created:
            try:
                WorkflowType.new_workflow_item("demo", instance)
            except Exception:
                pass


tag_CHOICE = [
    ("0", "Standard"),
    ("1", "Important"),
]


class Example1User(models.Model):
    """
    Simple user model for table demos.

    Stores a username and email address with no custom behavior.
    """

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "tables_demo"

        ordering = ["id"]

    username = models.CharField(
        "User name", null=False, blank=False, editable=True, max_length=64
    )
    email = models.EmailField(
        "Email",
        null=True,
        blank=True,
        editable=True,
    )


admin_register(Example1User)


class Example1Computer(models.Model):
    """
    Computer inventory model with serial number, IP, and active status.

    Stores a serial number, description, IP address, and active boolean
    flag. Serves as the parent model for Example2Peripheral and proxy models.
    """

    class Meta:
        verbose_name = _("Computer")
        verbose_name_plural = _("Computers")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "tables_demo"

        ordering = ["id"]

    sn = models.CharField(
        "Serial number", null=False, blank=False, editable=True, max_length=64
    )
    description = models.CharField(
        "Description", null=False, blank=False, editable=True, max_length=64
    )
    ip = models.GenericIPAddressField(
        "IP",
        null=True,
        blank=True,
        editable=True,
    )
    active = models.BooleanField(
        "Active",
        null=False,
        blank=False,
        editable=True,
        default=False,
    )


admin_register(Example1Computer)


class Example2Peripheral(models.Model):
    """
    Child table model linked to Example1Computer via a foreign key.

    Represents a peripheral device belonging to a computer, storing a
    parent FK and description.
    """

    class Meta:
        verbose_name = _("Peripheral")
        verbose_name_plural = _("Peripherals")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "tables_demo"

        ordering = ["id"]

    parent = ext_models.PtigForeignKey(
        Example1Computer,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Parent",
    )
    description = models.CharField(
        "Description", null=False, blank=False, editable=True, max_length=64
    )


admin_register(Example2Peripheral)


class Example3Tag(models.Model):
    """
    Tagging model with context-sensitive initialization and filtering.

    Stores a choice-based tag, description, and references to the tagged
    app/table/parent_id. ``init_new()`` parses a compound value to preset
    the context; ``filter()`` scopes the queryset by app, table, and parent.
    """

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "tables_demo"

        ordering = ["id"]

    tag = models.CharField(
        "Tag", null=False, blank=False, editable=True, choices=tag_CHOICE, max_length=64
    )
    description = models.CharField(
        "Description", null=True, blank=True, editable=True, max_length=64
    )
    app = models.CharField(
        "Application", null=False, blank=False, editable=True, max_length=64
    )
    table = models.CharField(
        "Table", null=True, blank=True, editable=True, max_length=64
    )
    parent_id = models.IntegerField(
        "Parent id",
        null=True,
        blank=True,
        editable=True,
    )

    def init_new(self, request, view, value=None):
        if value:
            try:
                app, tbl, pid = value.split("__")
                return {"app": app, "table": tbl, "parent_id": pid}
            except ValueError:
                pass
        return {"app": "default", "table": "default", "parent_id": 0}

    @classmethod
    def filter(cls, value, view=None, request=None):
        if value:
            try:
                app, tbl, pid = value.split("__")
                return cls.objects.filter(app=app, table=tbl, parent_id=pid)
            except ValueError:
                pass
        return cls.objects.all()


admin_register(Example3Tag)


class Example4Parameter(JSONModel):
    """
    JSON-extensible parameter model with dynamic form fields.

    Stores a key and optional JSON data. ``get_form_class()`` dynamically
    adds CharField fields from stored JSON keys, and ``post_form()`` saves
    submitted values back into the JSON store.
    """

    class Meta:
        verbose_name = _("Parameter")
        verbose_name_plural = _("Parameters")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "tables_demo"

        ordering = ["id"]

    key = models.CharField("Key", null=False, blank=False, editable=True, max_length=32)

    def get_form_class(self, view, request, create):
        from django import forms

        base_form = view.get_form_class()
        data = self.get_json_data()

        class form_class(base_form):
            def __init__(inner_self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if data:
                    for key, value in data.items():
                        inner_self.fields[f"json_{key}"] = forms.CharField(
                            label=key, initial=value
                        )
                else:
                    inner_self.fields["json_test1"] = forms.CharField(
                        label="test1", initial="value_test1"
                    )
                    inner_self.fields["json_test2"] = forms.CharField(
                        label="test2", initial="value_test2"
                    )

        return form_class

    def post_form(self, view, form, request):
        data = form.cleaned_data
        if "json_test1" in data:
            self.json_test1 = data["json_test1"]
        if "json_test2" in data:
            self.json_test2 = data["json_test2"]
        return True

    def __str__(self):
        return self.key


admin_register(Example4Parameter)


class Example5ParamGroup(TreeModel):
    """
    Tree-structured parameter group model.

    Supports hierarchical nesting via a PtigTreeForeignKey to self,
    with two required FK fields (main_parameter, second_parameter) and
    an M2M field (parameters) all pointing to Example4Parameter.
    """

    class Meta:
        verbose_name = _("Group of parameters")
        verbose_name_plural = _("Groups of parameters")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "tables_demo"

        ordering = ["id"]

    parent = ext_models.PtigTreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        editable=True,
        verbose_name="Parent",
    )
    main_parameter = ext_models.PtigForeignKey(
        Example4Parameter,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Main parameter",
    )
    second_parameter = ext_models.PtigForeignKey(
        Example4Parameter,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Second parameter",
        related_name="second_parameters",
        search_fields=[
            "key__startswith",
        ],
    )
    parameters = ext_models.PtigManyToManyField(
        Example4Parameter,
        editable=True,
        verbose_name="Parameters",
        related_name="group_parameters",
    )


admin_register(Example5ParamGroup)


class Example6ComputerFromExample1(Example1Computer):
    """
    Proxy model of Example1Computer providing an alternate table view.

    Shares the same data with no additional fields or methods, allowing
    a different presentation configuration.
    """

    class Meta:
        verbose_name = _("Proxy to computer")
        verbose_name_plural = _("Proxy to computers")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "tables_demo"

        ordering = ["id"]

        proxy = True


admin_register(Example6ComputerFromExample1)


class Example7ComputerFromExample1(Example1Computer):
    """
    Proxy model of Example1Computer with custom table action handling.

    Overrides ``table_action()`` to handle insert_rows by refreshing the
    view, while delegating copy/paste/delete to the standard action handler.
    """

    class Meta:
        verbose_name = _("Proxy to computer")
        verbose_name_plural = _("Proxy to computers")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "tables_demo"

        ordering = ["id"]

        proxy = True

    @classmethod
    def table_action(cls, list_view, request, data):
        if data.get("action") == "insert_rows":
            return actions.refresh(request)
        return standard_table_action(
            cls, list_view, request, data, ["copy", "paste", "delete"]
        )


admin_register(Example7ComputerFromExample1)
