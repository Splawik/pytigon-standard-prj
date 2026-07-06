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

device_type_choices = [
    ("C", "Computer"),
    ("M", "Monitor"),
    ("P", "Printer"),
    ("O", "Other"),
    ("H", "Phone"),
]

status_choice = [
    ("A", "Active"),
    ("R", "Removed"),
    ("S", "Scrapped"),
]

monitor_type_choices = [
    ("S", "Standard"),
    ("P", "Proffesional"),
]

printer_type_choices = [
    ("D", "Dot matrix"),
    ("I", "Inkjet"),
    ("L", "Laser"),
]

computer_type_choice = [
    ("D", "Desktop computer"),
    ("S", "Server"),
    ("L", "Laptop"),
    ("T", "Tablet"),
]

other_type_choice = [
    ("U", "Ups"),
    ("R", "Router"),
    ("S", "Switch"),
    ("W", "Wifi router"),
    ("T", "Telephone exchange"),
    ("P", "Projector"),
    ("O", "Other"),
]

phone_type_choice = [
    ("M", "Mobile"),
    ("L", "Landline"),
    ("S", "Smartphone"),
]


class Device(schelements.models.Element):

    class Meta:
        verbose_name = _("Device")
        verbose_name_plural = _("Device")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schhardware"

        ordering = ["id"]

        abstract = False

    serial_number = models.CharField(
        "Serial number", null=False, blank=False, editable=True, max_length=64
    )
    purchase_date = models.DateField(
        "Purchase date",
        null=True,
        blank=True,
        editable=True,
    )
    guarantee_date = models.DateField(
        "Guarantee date", null=True, blank=True, editable=True, max_length=32
    )
    device_type = models.CharField(
        "Device type",
        null=False,
        blank=False,
        editable=True,
        choices=device_type_choices,
        max_length=1,
    )
    manufacturer = models.CharField(
        "Manufacturer", null=True, blank=True, editable=True, max_length=64
    )
    model = models.CharField(
        "Model", null=True, blank=True, editable=True, max_length=64
    )
    operators = models.CharField(
        "Operators", null=True, blank=True, editable=True, max_length=256
    )
    status = models.CharField(
        "Status",
        null=False,
        blank=False,
        editable=True,
        choices=status_choice,
        max_length=1,
    )

    def init_new(self, request, view, param=None):
        return {
            "type": "I-DEV",
        }

    def transform_form(self, form, new):
        form.fields["type"].widget = form.fields["type"].hidden_widget()
        form.fields["device_type"].widget = form.fields["device_type"].hidden_widget()

    def get_form_class(self, view, request, create):
        base_form = view.get_form_class()

        class form_class(base_form):
            class Meta(base_form.Meta):
                labels = {
                    "code": _("Identyfication number"),
                }

        return form_class


class StandardComputer(Device):

    class Meta:
        verbose_name = _("Computer")
        verbose_name_plural = _("Computer")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schhardware"

        ordering = ["id"]

        abstract = True

    ram = models.IntegerField(
        "RAM",
        null=True,
        blank=True,
        editable=True,
    )
    hdd = models.IntegerField(
        "HDD",
        null=True,
        blank=True,
        editable=True,
    )
    processor = models.CharField(
        "Processor", null=True, blank=True, editable=True, max_length=32
    )
    working_group = models.CharField(
        "Working group", null=True, blank=True, editable=True, max_length=32
    )
    net_name = models.CharField(
        "Network name", null=True, blank=True, editable=True, max_length=32
    )
    ip = models.GenericIPAddressField(
        "IP address",
        null=True,
        blank=True,
        editable=True,
    )
    mac = models.CharField(
        "Mac address", null=True, blank=True, editable=True, max_length=32
    )
    use = models.CharField("Use", null=True, blank=True, editable=True, max_length=256)
    computer_type = models.CharField(
        "Computer type",
        null=False,
        blank=False,
        editable=True,
        choices=computer_type_choice,
        max_length=1,
    )

    def save(self, force_insert=False, force_update=False):
        self.device_type = "C"
        super().save(force_insert, force_update)

    def init_new(self, request, view, param=None):
        return {"type": "I-DEV-C", "device_type": "C"}


class StandardMonitor(Device):

    class Meta:
        verbose_name = _("Monitor")
        verbose_name_plural = _("Monitor")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schhardware"

        ordering = ["id"]

        abstract = True

    size = models.IntegerField(
        "Size of screen",
        null=True,
        blank=True,
        editable=True,
    )
    monitor_type = models.CharField(
        "Monitor type",
        null=False,
        blank=False,
        editable=True,
        choices=monitor_type_choices,
        max_length=1,
    )

    def save(self, force_insert=False, force_update=False):
        self.device_type = "M"
        super().save(force_insert, force_update)

    def init_new(self, request, view, param=None):
        return {"type": "I-DEV-M", "device_type": "M"}


class StandardPrinter(Device):

    class Meta:
        verbose_name = _("Printer")
        verbose_name_plural = _("Printer")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schhardware"

        ordering = ["id"]

        abstract = True

    printer_type = models.CharField(
        "Printer type",
        null=False,
        blank=False,
        editable=True,
        choices=printer_type_choices,
        max_length=1,
    )

    def save(self, force_insert=False, force_update=False):
        self.device_type = "P"
        super().save(force_insert, force_update)

    def init_new(self, request, view, param=None):
        return {"type": "I-DEV-P", "device_type": "P"}


class StandardPhone(Device):

    class Meta:
        verbose_name = _("Phone")
        verbose_name_plural = _("Phones")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schhardware"

        ordering = ["id"]

        abstract = True

    phone_type = models.CharField(
        "Phone type",
        null=False,
        blank=False,
        editable=True,
        default="S",
        choices=phone_type_choice,
        max_length=1,
    )
    operator = models.CharField(
        "Operator", null=True, blank=True, editable=True, max_length=32
    )
    phone_number = models.CharField(
        "Phone number", null=True, blank=True, editable=True, max_length=32
    )

    def save(self, force_insert=False, force_update=False):
        self.device_type = "O"
        super().save(force_insert, force_update)

    def init_new(self, request, view, param=None):
        return {"type": "I-DEV-O", "device_type": "O"}


class StandardOtherDevice(Device):

    class Meta:
        verbose_name = _("Other device")
        verbose_name_plural = _("Other devices")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schhardware"

        ordering = ["id"]

        abstract = True

    other_type = models.CharField(
        "Other device type",
        null=True,
        blank=True,
        editable=True,
        choices=other_type_choice,
        max_length=1,
    )

    def save(self, force_insert=False, force_update=False):
        self.device_type = "H"
        super().save(force_insert, force_update)

    def init_new(self, request, view, param=None):
        return {"type": "I-DEV-H", "device_type": "H"}


class Computer(StandardComputer):

    class Meta:
        verbose_name = _("Computer")
        verbose_name_plural = _("Computers")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schhardware"

        ordering = ["id"]


admin_register(Computer)


class Monitor(StandardMonitor):

    class Meta:
        verbose_name = _("Monitor")
        verbose_name_plural = _("Monitors")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schhardware"

        ordering = ["id"]


admin_register(Monitor)


class Printer(StandardPrinter):

    class Meta:
        verbose_name = _("Printer")
        verbose_name_plural = _("Printers")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schhardware"

        ordering = ["id"]


admin_register(Printer)


class Phone(StandardPhone):

    class Meta:
        verbose_name = _("Phone")
        verbose_name_plural = _("Phones")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schhardware"

        ordering = ["id"]


admin_register(Phone)


class OtherDevice(StandardOtherDevice):

    class Meta:
        verbose_name = _("OtherDevice")
        verbose_name_plural = _("OtherDevices")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schhardware"

        ordering = ["id"]


admin_register(OtherDevice)


e = schelements.models.Element
e.add_type("I-DEV-C", "Item/Device/Computer", "Computers", "Computer", "schhardware")
e.add_type("I-DEV-M", "Item/Device/Monitor", "Monitors", "Monitor", "schhardware")
e.add_type("I-DEV-P", "Item/Device/Printer", "Printers", "Printer", "schhardware")
e.add_type("I-DEV-H", "Item/Device/Phone", "Phones", "Phone", "schhardware")
e.add_type(
    "I-DEV-O", "Item/Device/Other", "Other devices", "Otherdevice", "schhardware"
)
