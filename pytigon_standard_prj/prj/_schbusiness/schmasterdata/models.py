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

import schelements.models


from django.db.models import Q
from pytigon_lib.schtools.tools import update_nested_dict

UnitTypeChoices = [
    ("1", "main unit"),
    ("2", "for sale"),
]

BankAccountTypeChoice = [
    ("0", "Disabled"),
    ("1", "Active and default"),
    ("2", "Active"),
]


class StandardCompany(schelements.models.Element):

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]

        abstract = True

    element_ptr = models.OneToOneField(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Element ptr",
        parent_link=True,
        related_name="%(app_label)s_%(class)s_related",
    )

    def save(self, force_insert=False, force_update=False):
        self.type = "O-COM"
        super().save(force_insert, force_update)

    def init_new(self, request, view, param=None):
        return {"type": "O-COM"}


class StandardCustomer(schelements.models.Element):

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]

        abstract = True

    element_ptr = models.OneToOneField(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=False,
        verbose_name="Element ptr",
        parent_link=True,
        related_name="%(app_label)s_%(class)s_related",
    )
    id_number2 = models.CharField(
        "ID number 2", null=True, blank=True, editable=True, max_length=32
    )
    id_number3 = models.CharField(
        "ID number 3", null=True, blank=True, editable=True, max_length=32
    )
    country = models.CharField(
        "Country", null=True, blank=True, editable=True, max_length=64
    )
    zip_code = models.CharField(
        "Zip code", null=True, blank=True, editable=True, max_length=16
    )
    post = models.CharField("Post", null=True, blank=True, editable=True, max_length=64)
    city = models.CharField("City", null=True, blank=True, editable=True, max_length=64)
    street = models.CharField(
        "Street", null=True, blank=True, editable=True, max_length=64
    )
    house_number = models.CharField(
        "House number", null=True, blank=True, editable=True, max_length=16
    )
    apartment_number = models.CharField(
        "Apartment number", null=True, blank=True, editable=True, max_length=16
    )
    limit = models.DecimalField(
        "Limit",
        null=True,
        blank=True,
        editable=True,
        default=0,
        max_digits=19,
        decimal_places=2,
    )
    payment_type = models.CharField(
        "Payment type", null=True, blank=True, editable=True, max_length=16
    )
    payment_days = models.IntegerField(
        "Payment days",
        null=True,
        blank=True,
        editable=True,
    )
    individual = models.BooleanField(
        "Individual",
        null=True,
        blank=True,
        editable=True,
        default=False,
    )
    blockade = models.BooleanField(
        "Sale block",
        null=False,
        blank=False,
        editable=True,
        default=False,
    )

    def save(self, force_insert=False, force_update=False):
        self.type = "O-CUS"
        super().save(force_insert, force_update)

    def init_new(self, request, view, param=None):
        return {"type": "O-CUS"}

    def get_form_class(self, view, request, create):
        base_form = view.get_form_class()

        class form_class(base_form):
            class Meta(base_form.Meta):
                labels = {
                    "code": _("Tax Identification Number"),
                }

        return form_class


class StandardSupplier(schelements.models.Element):

    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]

        abstract = True

    element_ptr = models.OneToOneField(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Element ptr",
        parent_link=True,
        related_name="%(app_label)s_%(class)s_related",
    )
    id_number2 = models.CharField(
        "ID number 2", null=True, blank=True, editable=True, max_length=32
    )
    id_number3 = models.CharField(
        "ID number 3", null=True, blank=True, editable=True, max_length=32
    )
    country = models.CharField(
        "Country", null=True, blank=True, editable=True, max_length=64
    )
    zip_code = models.CharField(
        "Zip code", null=True, blank=True, editable=True, max_length=16
    )
    post = models.CharField("Post", null=True, blank=True, editable=True, max_length=64)
    city = models.CharField("City", null=True, blank=True, editable=True, max_length=64)
    street = models.CharField(
        "Street", null=True, blank=True, editable=True, max_length=64
    )
    house_number = models.CharField(
        "House number", null=True, blank=True, editable=True, max_length=16
    )
    apartment_number = models.CharField(
        "Apartment number", null=True, blank=True, editable=True, max_length=16
    )
    payment_type = models.CharField(
        "Payment type", null=True, blank=True, editable=True, max_length=16
    )
    payment_days = models.IntegerField(
        "Payment days",
        null=True,
        blank=True,
        editable=True,
    )

    def save(self, force_insert=False, force_update=False):
        self.type = "O-SUP"
        super().save(force_insert, force_update)

    def init_new(self, request, view, param=None):
        return {"type": "O-SUP"}

    def get_form_class(self, view, request, create):
        base_form = view.get_form_class()

        class form_class(base_form):
            class Meta(base_form.Meta):
                labels = {
                    "code": _("Tax Identification Number"),
                }

        return form_class


class StandardProduct(schelements.models.Element):

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]

        abstract = True

    element_ptr = models.OneToOneField(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Element ptr",
        parent_link=True,
        related_name="%(app_label)s_%(class)s_related",
    )
    tax_rate = models.CharField(
        "Tax rate", null=True, blank=True, editable=True, max_length=16
    )
    name_2 = models.CharField(
        "Name 2", null=False, blank=False, editable=True, max_length=128
    )
    code_2 = models.CharField(
        "Code 2", null=False, blank=False, editable=True, max_length=32
    )
    code_3 = models.CharField(
        "Code 3", null=False, blank=False, editable=True, max_length=32
    )
    stock = models.BooleanField(
        "Stock",
        null=False,
        blank=False,
        editable=True,
        default=False,
    )
    uom_code = models.CharField(
        "Unit of measurement code",
        null=False,
        blank=False,
        editable=True,
        default="piece",
        max_length=32,
    )

    def save(self, force_insert=False, force_update=False):
        self.type = "I-PRD"
        super().save(force_insert, force_update)

    def init_new(self, request, view, param=None):
        return {"type": "I-PRD"}


class StandardMerchandise(schelements.models.Element):

    class Meta:
        verbose_name = _("Merchandise")
        verbose_name_plural = _("Merchandises")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]

        abstract = True

    element_ptr = models.OneToOneField(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Element ptr",
        parent_link=True,
        related_name="%(app_label)s_%(class)s_related",
    )
    tax_rate = models.CharField(
        "Tax rate", null=False, blank=False, editable=True, max_length=16
    )
    name_2 = models.CharField(
        "Name 2", null=False, blank=False, editable=True, max_length=128
    )
    code_2 = models.CharField(
        "Code 2", null=False, blank=False, editable=True, max_length=32
    )
    code_3 = models.CharField(
        "Code 3", null=False, blank=False, editable=True, max_length=32
    )
    stock = models.BooleanField(
        "Stock",
        null=False,
        blank=False,
        editable=True,
        default=False,
    )
    uom_code = models.CharField(
        "Unit of measurement code",
        null=False,
        blank=False,
        editable=True,
        default="piece",
        max_length=32,
    )

    def save(self, force_insert=False, force_update=False):
        self.type = "I-MER"
        super().save(force_insert, force_update)

    def init_new(self, request, view, param=None):
        return {"type": "I-MER"}


class StandardUnitOfMeasure(schelements.models.Element):

    class Meta:
        verbose_name = _("Unit of measure")
        verbose_name_plural = _("Units of measure")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]

        abstract = True

    element_ptr = models.OneToOneField(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Element ptr",
        parent_link=True,
        related_name="%(app_label)s_%(class)s_related",
    )
    precision = models.IntegerField(
        "Precision",
        null=False,
        blank=False,
        editable=True,
        default=2,
    )

    def save(self, force_insert=False, force_update=False):
        self.type = "C-UNT"
        super().save(force_insert, force_update)

    def init_new(self, request, view, param=None):
        return {"type": "C-UNT"}


class StandardEmployee(schelements.models.Element):

    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]

        abstract = True

    element_ptr = models.OneToOneField(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Element ptr",
        parent_link=True,
        related_name="%(app_label)s_%(class)s_related",
    )
    first_name = models.CharField(
        "First name", null=False, blank=False, editable=True, max_length=32
    )
    surname = models.CharField(
        "Surname", null=False, blank=False, editable=True, max_length=64
    )
    workplace = models.CharField(
        "Workplace", null=True, blank=True, editable=True, max_length=64
    )
    email = models.EmailField(
        "Email",
        null=True,
        blank=True,
        editable=True,
    )
    phone_number = models.CharField(
        "Phone number", null=True, blank=True, editable=True, max_length=64
    )
    address = models.CharField(
        "Address", null=True, blank=True, editable=True, max_length=128
    )
    other_contact = models.CharField(
        "Other contact", null=True, blank=True, editable=True, max_length=128
    )

    def save(self, force_insert=False, force_update=False):
        self.type = "O-EMP"
        super().save(force_insert, force_update)

    def init_new(self, request, view, param=None):
        return {"type": "O-EMP"}


class StandardPerson(schelements.models.Element):

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]

        abstract = True

    element_ptr = models.OneToOneField(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Element ptr",
        parent_link=True,
        related_name="%(app_label)s_%(class)s_related",
    )
    first_name = models.CharField(
        "First name", null=True, blank=True, editable=True, max_length=32
    )
    surname = models.CharField(
        "Surname", null=True, blank=True, editable=True, max_length=64
    )
    email = models.EmailField(
        "Email",
        null=True,
        blank=True,
        editable=True,
    )
    phone_number = models.CharField(
        "Phone number", null=True, blank=True, editable=True, max_length=64
    )
    address = models.CharField(
        "Address", null=True, blank=True, editable=True, max_length=128
    )
    other_contact = models.CharField(
        "Other contact", null=True, blank=True, editable=True, max_length=128
    )

    def save(self, force_insert=False, force_update=False):
        self.type = "O-PER"
        super().save(force_insert, force_update)

    def init_new(self, request, view, param=None):
        return {"type": "O-PER"}


class StandardLocation(schelements.models.Element):

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]

        abstract = True

    element_ptr = models.OneToOneField(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Element ptr",
        parent_link=True,
        related_name="%(app_label)s_%(class)s_related",
    )
    address = models.CharField(
        "Address", null=True, blank=True, editable=True, max_length=128
    )

    def save(self, force_insert=False, force_update=False):
        self.type = "O-LOC"
        super().save(force_insert, force_update)

    def init_new(self, request, view, param=None):
        return {"type": "O-LOC"}


class UnitOfMeasure4Product(models.Model):

    class Meta:
        verbose_name = _("Unit of measure for the product")
        verbose_name_plural = _("Units of measure for the product")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]

    parent = ext_models.PtigForeignKey(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Parent",
        related_name="unitofmeasure4product_set2",
        limit_choices_to=Q(type__startswith="I-PRD") | Q(type__startswith="I-MER"),
    )
    unit_of_measure = ext_models.PtigForeignKey(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Unit of measure",
        limit_choices_to={"type__startswith": "C-UNT"},
    )
    description = models.CharField(
        "Description", null=False, blank=False, editable=True, max_length=128
    )
    converter = models.FloatField(
        "converter to the main unit",
        null=False,
        blank=False,
        editable=True,
        default=1,
    )
    unit_type = models.CharField(
        "Unit type",
        null=True,
        blank=True,
        editable=True,
        choices=UnitTypeChoices,
        max_length=1,
    )


admin_register(UnitOfMeasure4Product)


class Bank4Contractor(models.Model):

    class Meta:
        verbose_name = _("Bank for contractor")
        verbose_name_plural = _("Banks for contractors")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]

    parent = ext_models.PtigForeignKey(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Parent",
    )
    name = models.CharField(
        "Name", null=False, blank=False, editable=True, max_length=64
    )
    account_number = models.CharField(
        "Account number", null=False, blank=False, editable=True, max_length=64
    )
    status = models.CharField(
        "Status",
        null=False,
        blank=False,
        editable=True,
        default=1,
        choices=BankAccountTypeChoice,
        max_length=1,
    )


admin_register(Bank4Contractor)


class Company(StandardCompany):

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]


admin_register(Company)


class Customer(StandardCustomer):

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]


admin_register(Customer)


class Supplier(StandardSupplier):

    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]


admin_register(Supplier)


class Product(StandardProduct):

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]


admin_register(Product)


class Merchandise(StandardMerchandise):

    class Meta:
        verbose_name = _("Merchandise")
        verbose_name_plural = _("Merchandises")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]


admin_register(Merchandise)


class UnitOfMeasure(StandardUnitOfMeasure):

    class Meta:
        verbose_name = _("Unit of measure")
        verbose_name_plural = _("Units of measure")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]


admin_register(UnitOfMeasure)


class Employee(StandardEmployee):

    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Workers")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]


admin_register(Employee)


class Person(StandardPerson):

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]


admin_register(Person)


class Location(StandardLocation):

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schmasterdata"

        ordering = ["id"]


admin_register(Location)


STRUCTURE = {
    "O-COM": {"table": "Company", "app": "schmasterdata"},
    "O-CUS": {"table": "Customer", "app": "schmasterdata"},
    "O-SUP": {"table": "Supplier", "app": "schmasterdata"},
    "I-PRD": {"table": "Product", "app": "schmasterdata"},
    "I-MER": {"table": "Merchandise", "app": "schmasterdata"},
    "C-UNT": {"table": "UnitOfMeasure", "app": "schmasterdata"},
    "O-EMP": {"table": "Employee", "app": "schmasterdata"},
    "O-PER": {"table": "Person", "app": "schmasterdata"},
    "O-LOC": {"table": "Location", "app": "schmasterdata"},
}

update_nested_dict(schelements.models.Element.get_structure(), STRUCTURE)
