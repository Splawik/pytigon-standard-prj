from django.db import models
from django.utils.translation import gettext_lazy as _

from pytigon_lib.schdjangoext.fields import *
import pytigon_lib.schdjangoext.fields as ext_models
from pytigon_lib.schdjangoext.models import *

import tables_demo.models


from tables_demo.models import *
from django.forms import fields as form_fields


GenreChoices = [
    ("r", "Rock"),
    ("p", "Pop"),
    ("j", "Jazz"),
    ("h", "Heavy Metal"),
    ("e", "Elekctonic"),
    ("c", "Classical"),
    ("o", "Other"),
]


class Album(models.Model):
    """
    Music album model with custom table filtering and sorting.

    Stores release date, artist, description, and genre. Overrides
    ``filter()`` for genre-based queryset filtering, ``init_new()`` to
    preset the genre, ``sort()`` for custom ordering, and
    ``get_form_class()`` to add a Textarea widget to the description field.
    """

    class Meta:
        verbose_name = _("Album")
        verbose_name_plural = _("Albums")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "tables_adv_demo"

        ordering = ["id"]

    release_date = models.DateField(
        "Release date",
        null=True,
        blank=True,
        editable=True,
    )
    artist = models.CharField(
        "Artist", null=True, blank=True, editable=True, max_length=64
    )
    description = models.CharField(
        "Description", null=False, blank=False, editable=True, max_length=256
    )
    genre = models.CharField(
        "Genre",
        null=False,
        blank=False,
        editable=True,
        choices=GenreChoices,
        max_length=2,
    )

    @classmethod
    def filter(cls, value, view=None, request=None):
        if value:
            return cls.objects.filter(genre=value)
        return cls.objects.all()

    def init_new(self, request, view, value=None):
        if value:
            return {"genre": value}
        return {}

    @staticmethod
    def sort(queryset, sort, order):
        if sort:
            return queryset.order_by(sort if order == "asc" else f"-{sort}")
        return queryset

    def get_form_class(self, view, request, create):
        base_form = view.get_form_class()

        class form_class(base_form):
            class Meta(base_form.Meta):
                widgets = {
                    "description": form_fields.Textarea(attrs={"cols": 80, "rows": 3}),
                }

        return form_class


admin_register(Album)


class AlbumProxy(Album):
    """
    Proxy model of Album providing an alternative table presentation.

    Shares the same underlying data as Album with no additional fields or
    methods, allowing a different view configuration.
    """

    class Meta:
        verbose_name = _("Album")
        verbose_name_plural = _("Albums")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "tables_adv_demo"

        ordering = ["id"]

        proxy = True


admin_register(AlbumProxy)


class UserGroup(models.Model):
    """
    Pivot/join model serving as a many-to-many intermediary table.

    Declares no explicit fields; used by the framework as a linking
    table for complex many-to-many relationships.
    """

    class Meta:
        verbose_name = _("User group")
        verbose_name_plural = _("User groups")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "tables_adv_demo"

        ordering = ["id"]


admin_register(UserGroup)


class Track(models.Model):
    """
    Music track child model linked to an Album parent.

    Stores a track name, a parent FK to Album, a single FK to
    Example4Parameter (``param``), and an M2M relation to
    Example4Parameter (``params``).
    """

    class Meta:
        verbose_name = _("Track")
        verbose_name_plural = _("Tracks")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "tables_adv_demo"

        ordering = ["id"]

    parent = ext_models.PtigForeignKey(
        Album,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Parent",
    )
    name = models.CharField(
        "Name", null=False, blank=False, editable=True, max_length=64
    )
    param = ext_models.PtigForeignKey(
        tables_demo.models.Example4Parameter,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        editable=True,
        verbose_name="Param",
        search_fields=[
            "key__icontains",
        ],
        can_add=False,
    )
    params = ext_models.PtigManyToManyField(
        tables_demo.models.Example4Parameter,
        editable=True,
        verbose_name="Parameters",
        search_fields=[
            "key__icontains",
        ],
        related_name="track_parameters",
    )


admin_register(Track)
