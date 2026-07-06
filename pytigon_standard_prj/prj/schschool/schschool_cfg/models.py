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

import schhardware.models


from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.db.models import Q
from django.core.management.utils import get_random_secret_key
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django import forms

from allauth.account.forms import EmailAwarePasswordResetTokenGenerator
from allauth.account.utils import user_pk_to_url_str
from allauth.utils import build_absolute_uri

from pytigon_lib.schtools.tools import get_request, update_nested_dict
from pytigon_lib.schdjangoext.email import send_message

import schelements.models
import schprofile.models
import school.models
import schmasterdata.models
import schlabels.models

from schprofile.models import init_user_profiles, Profile


def get_teachers():
    return schelements.models.Element.limit_choices("N", "O-SUP")


def get_students():
    return schelements.models.Element.limit_choices("N", "O-CUS")


schelements.models.Element.add_type(
    "O-CUS-S", "Owner/Customer/Student", "Students", "Student", "school"
)
schelements.models.Element.add_type(
    "O-SUP-T", "Owner/Supplier/Teacher", "Teachers", "Teacher", "school"
)
schelements.models.Element.add_type(
    "O-EMP-A",
    "Owner/Employee/Administrator",
    "Administrators",
    "Administrator",
    "school",
)
schelements.models.Element.add_type(
    "I-GRP-D", "Item/Group/Device", "Groups of devices", "IGroupDevice", "school"
)


STRUCTURE = {
    "ROOT": {"next": ["O-COM", "O-GRP", "I-GRP", "I-GRP-D", "C-GRP"]},
    "O-COM": {
        "next": [
            "O-EMP",
        ],
        "title": "School",
        "table": "School",
        "app": "school",
    },
    "O-DIV": {
        "next": [
            "O-CUS",
            "O-CUS-S",
        ],
        "title": "Class",
        "table": "Class",
        "app": "school",
    },
    "O-GRP": {
        "next": ["O-SUP", "O-SUP-T"],
        "title": "Group of elements",
        "table": "OGroup",
        "app": "school",
    },
    "I-GRP": {
        "title": "Group of items",
        "table": "IGroup",
        "app": "school",
        "next": [
            "I-INT",
            "I-CUR",
        ],
    },
    "I-GRP-D": {
        "next": ["I-DEV-C", "I-DEV-M", "I-DEV-P", "I-DEV-H", "I-DEV-O"],
    },
    "C-GRP": {
        "title": "Config group",
        "table": "CGroup",
        "app": "school",
        "next": [
            "C-GRP",
            "C-UNT",
        ],
    },
}

update_nested_dict(schelements.models.Element.get_structure(), STRUCTURE)


class SchoolElement:
    def save(self, *argi, **argv):
        # if not self.parent:
        #    if self.type in GROUP_FOR_TYPE:
        #        self.parent = GROUP_FOR_TYPE[self.type]
        super().save(*argi, **argv)

    @staticmethod
    def filter_by_permissions(view, queryset_or_obj, request):
        # if queryset_or_obj != None:
        #    print(queryset_or_obj.model)
        #    if queryset_or_obj.model == SchoolElement:
        #        return schelements.models.Element.objects.filter(
        #            type__in=schelements.models.Element.get_structure().keys()
        #        )
        return queryset_or_obj

    @classmethod
    def filter(cls, value, view=None, request=None):
        ret = None
        if value and value != "-":
            try:
                i = int(value)
                if i >= 0:
                    if i == 0:
                        ret = schelements.models.Element.objects.filter(parent=None)
                    else:
                        ret = schelements.models.Element.objects.filter(parent=i)
                else:
                    ret = schelements.models.Element.objects.filter(parent__id=i * -1)
            except:
                ret = schelements.models.Element.objects.filter(type=value)
        else:
            ret = schelements.models.Element.objects.all()

        x = view.kwargs["target"].split("__")
        if len(x) == 3:
            if x[-1] == "all_devices":
                ret = ret.filter(
                    Q(type__startswith="I-DEV")
                    | Q(
                        type__in=(
                            "I-GRP",
                            "I-GRP-D",
                            "O-COM",
                            "O-LOC",
                        )
                    )
                    | Q(type="O-GRP", parent__type__in=("O-GRP", "O-COM", "O-LOC"))
                )

        return ret

    @staticmethod
    def has_the_right(perm, kwargs, request):
        return True


extend_class(schelements.models.Element, SchoolElement)


class Product:
    def get_form(self, view, request, form_class, adding=False):
        obj = self
        internet_sale = (
            schlabels.models.ElementLabel.has_label(self, "internet_sale")
            if self.pk
            else False
        )

        class form_class2(form_class):
            def __init__(self, *args, **kwargs):
                nonlocal internet_sale
                super().__init__(*args, **kwargs)
                self.fields["internet_sale"] = forms.BooleanField(
                    label="Internet sale", initial=internet_sale, required=False
                )

            def _save_m2m(self, *argi, **argv):
                nonlocal obj, internet_sale
                ret = super()._save_m2m(*argi, **argv)
                internet_sale = self.cleaned_data["internet_sale"]
                if internet_sale:
                    schlabels.models.ElementLabel.set_label(obj, "internet_sale")
                else:
                    schlabels.models.ElementLabel.remove_label(obj, "internet_sale")
                return ret

        return view.get_form(form_class2)


extend_class(schmasterdata.models.Product, Product)
extend_class(schmasterdata.models.Merchandise, Product)


def get_element_queryset():
    request = get_request()
    if request:
        if request.user.is_superuser:
            return None
        elif (
            hasattr(request.user, "profile")
            and request.user.profile
            and request.user.profile.owner
        ):
            return Q(first_ancestor=request.user.profile.owner.first_ancestor)
    else:
        return None
    return Q(pk=0)


schelements.models.GET_ELEMENT_QUERYSET.set_function(get_element_queryset)


# Module customization: _schdata.schelements - DocHead, DocItem


class SchoolDocHead:
    def save(self, *argi, **argv):
        super().save(*argi, **argv)

    @staticmethod
    def filter_by_permissions(view, queryset_or_obj, request):
        return queryset_or_obj

    @staticmethod
    def has_the_right(perm, kwargs, request):
        return True


extend_class(schelements.models.DocHead, SchoolDocHead)


class SchoolDocItem:
    def save(self, *argi, **argv):
        super().save(*argi, **argv)

    @staticmethod
    def filter_by_permissions(view, queryset_or_obj, request):
        return queryset_or_obj

    @staticmethod
    def has_the_right(perm, kwargs, request):
        return True


extend_class(schelements.models.DocItem, SchoolDocItem)


# Module customization: _schdata.schprofile


def limit_owner():
    return {"type__in": ("O-CUS", "O-CUS-S")}


def limit_config():
    return {"type": "C-DIC"}


schprofile.models.LIMIT_OWNER.set_function(limit_owner)
schprofile.models.LIMIT_CONFIG.set_function(limit_config)

init_user_profiles()


def add_user_to_group(user, group_name):
    groups = Group.objects.filter(name=group_name)
    if len(groups) < 1:
        g = Group()
        g.name = group_name
        g.save()
    else:
        g = groups[0]
    g.user_set.add(user)


def context_for_password_reset(user):
    request = get_request()
    if request:
        current_site = get_current_site(request)
        email = user.email
        token_generator = EmailAwarePasswordResetTokenGenerator()
        temp_key = token_generator.make_token(user)
        path = reverse(
            "account_reset_password_from_key",
            kwargs=dict(uidb36=user_pk_to_url_str(user), key=temp_key),
        )
        url = build_absolute_uri(request, path)
        context = {
            "current_site": current_site,
            "user": user,
            "password_reset_url": url,
            "request": request,
        }
        return context
    return None


def add_user(user_obj, surname, name, email, user_type):
    user_model = get_user_model()
    user_objects = user_model.objects.filter(email=email)
    if not len(user_objects) > 0:
        user = user_model()
        user.username = email
        user.first_name = name
        user.last_name = surname
        user.email = email
        user.is_staff = False
        user.is_active = True
        user.is_superuser = False
        user.set_password(get_random_secret_key())
        user.save()

        user.profile.owner = user_obj
        user.profile.user_type = user_type
        user.profile.save()
    else:
        user = user_objects[0]
    context = context_for_password_reset(user)
    if context:
        context["user"] = user
    if user_type in ("STUDENT", "O-CUS-S"):
        add_user_to_group(user, "students")
        send_message(
            "Welcome to the program " + settings.PRJ_TITLE,
            "school/message_initial_student.html",
            settings.DEFAULT_FROM_EMAIL,
            (email,),
            None,
            context,
        )
    elif user_type in ("TEACHER", "O-SUP-T"):
        add_user_to_group(user, "teachers")
        send_message(
            "Welcome to the program " + settings.PRJ_TITLE,
            "school/message_initial_teacher.html",
            settings.DEFAULT_FROM_EMAIL,
            (email,),
            None,
            context,
        )
    elif user_type in ("ADMINISTRATOR", "O-EMP-A"):
        add_user_to_group(user, "admins")
        # send_message(
        #    "Welcome to the program " + settings.PRJ_TITLE,
        #    "school/message_initial_admin.html",
        #    settings.DEFAULT_FROM_EMAIL,
        #    (email,),
        #    None,
        #    context,
        # )


@receiver(post_save, sender=schmasterdata.models.StandardSupplier)
def supplier_created(sender, instance, created, **kwargs):
    print("supplier_created")


class Computer(schhardware.models.Computer):

    class Meta:
        verbose_name = _("Computer")
        verbose_name_plural = _("Computers")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schschool_cfg"

        ordering = ["id"]

    schmasterdata.models.StandardProduct._meta.get_field("grand_parent1").set(
        {
            "verbose_name": "School",
            "query": {"Q": Q(type="O-COM")},
            "search_fields": [
                "name__istartswith",
            ],
            "minimum_input_length": 0,
            "filter": "O-COM",
            "app_template": "school__school",
        }
    )

    if False:
        _f = schmasterdata.models.StandardProduct._meta.get_field("grand_parent1")
        _f.verbose_name = "School"
        _f.query = {"Q": Q(type="O-COM")}
        _f.search_fields = [
            "name__istartswith",
        ]
        _f.minimum_input_length = 0
        _f.filter = "O-COM"
        locals().pop("_f")


admin_register(Computer)


@receiver(pre_delete, sender=school.models.Student)
def delete_user(sender, instance, **kwargs):
    object_list = Profile.objects.filter(owner=instance)
    if len(object_list) > 0:
        object_list[0].user.delete()


def define_access_rules(user, rules):
    if user.is_superuser:
        return

    rules.allow("view", school.models.School, admin_email=user.email)
    rules.allow("view", school.models.School, code="SCHOOL2")

    if not user.is_authenticated:
        return

    rules.allow("change", school.models.School, code="SCHOOL5")
    rules.allow("view", schelements.models.Element)
    rules.allow("change", schelements.models.Element, code="SCHOOL5")
