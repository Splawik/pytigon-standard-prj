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
import schmasterdata.models


import datetime
from django.db.models import Q
from pytigon_lib.schviews import actions


def get_teachers():
    return schelements.models.Element.limit_choices("N", "O-SUP")


def get_students():
    return schelements.models.Element.limit_choices("N", "O-CUS")


class Class(schelements.models.Element):

    class Meta:
        verbose_name = _("Class")
        verbose_name_plural = _("Classes")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

        proxy = True

    @classmethod
    def table_action(cls, list_view, request, data):
        if "action" in data:
            if data["action"] == "insert_rows":
                table = data["table"]
                for row in table:
                    obj = Student()
                    surname = row[0].strip()
                    name = row[1].strip()
                    email = row[2].strip().lower()
                    if surname and name and email:
                        obj.name = (surname + " " + name).title()
                        obj.email = email
                        obj.type = "O-CUS"
                        obj.parent_id = list_view

                        if "filter" in list_view.kwargs and list_view.kwargs["filter"]:
                            obj.parent_id = int(list_view.kwargs["filter"])
                            obj.save()

                        # add_user(obj, surname, name, email, 'STUDENT')

                return actions.refresh(request)
        return standard_table_action(cls, list_view, request, data, ["copy", "paste"])


admin_register(Class)


class SubjectType(models.Model):

    class Meta:
        verbose_name = _("Subject type")
        verbose_name_plural = _("Subject types")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

    name = models.CharField(
        "Name",
        null=False,
        blank=False,
        editable=True,
        unique=True,
        db_index=True,
        max_length=128,
    )

    def __str__(self):
        return self.name


admin_register(SubjectType)


class Subject(models.Model):

    class Meta:
        verbose_name = _("Subject")
        verbose_name_plural = _("Subjects")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

    parent = ext_models.PtigForeignKey(
        Class,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Class",
    )
    subject_type = ext_models.PtigForeignKey(
        SubjectType,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Subject type",
    )
    description = models.CharField(
        "Description", null=False, blank=False, editable=True, max_length=128
    )
    max_number_of_lessons = models.IntegerField(
        "None",
        null=True,
        blank=True,
        editable=True,
    )

    def __str__(self):
        if self.description:
            return self.parent.code + "/" + self.description
        else:
            return self.parent.code + "/" + self.subject_type.name


admin_register(Subject)


class Teacher(schmasterdata.models.StandardSupplier):

    class Meta:
        verbose_name = _("Teacher")
        verbose_name_plural = _("Teachers")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

    email = models.CharField(
        "Email", null=False, blank=False, editable=True, max_length=64
    )
    subjects = ext_models.PtigManyToManyField(
        Subject,
        editable=True,
        verbose_name="Subjects",
        default=None,
        related_name="teacher_subjects",
    )

    def save(self, *argi, **argv):
        self.can_have_children = False

        super().save(*argi, **argv)

        x = self.name.split(" ", 1)
        if len(x) > 1:
            name = x[0]
            surname = x[1]
        else:
            name = ""
            surname = x


admin_register(Teacher)


class School(schmasterdata.models.StandardCompany):

    class Meta:
        verbose_name = _("School")
        verbose_name_plural = _("Schools")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

    admin = models.CharField(
        "Administrator", null=False, blank=False, editable=True, max_length=64
    )
    admin_email = models.EmailField(
        "Email (admin)",
        null=False,
        blank=False,
        editable=True,
    )

    def save(self, *argi, **argv):
        super().save(*argi, **argv)

        n_group = OGroup()
        n_group.parent = self
        n_group.type = "O-GRP"
        n_group.code = "N"
        n_group.name = "Nauczyciele"
        n_group.description = "Nauczyciele (O-SUP)"
        n_group.save()

        c_group = OGroup()
        c_group.parent = self
        c_group.type = "O-GRP"
        c_group.code = "C"
        c_group.name = "Klasy"
        c_group.description = "Klasy (O-DIV)"
        c_group.save()

        admin = Administrator.objects.filter(email=self.admin_email).first()
        if not admin:
            admin = Administrator()
            admin.parent = self
            admin.name = self.admin
            admin.email = self.admin_email
            admin.save()


admin_register(School)


class Student(schmasterdata.models.StandardCustomer):

    class Meta:
        verbose_name = _("Student")
        verbose_name_plural = _("Students")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

    email = models.EmailField(
        "Email",
        null=False,
        blank=False,
        editable=True,
        unique=True,
    )

    def save(self, *argi, **argv):
        print("SAVE__STUDENT!")
        super().save(*argi, **argv)

        x = self.name.split(" ", 1)
        if len(x) > 1:
            name = x[0]
            surname = x[1]
        else:
            name = ""
            surname = x
        # add_user(self, surname, name, self.email.lower(), 'STUDENT')


admin_register(Student)


class Grade(models.Model):

    class Meta:
        verbose_name = _("Grade")
        verbose_name_plural = _("Grades")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

    parent = ext_models.PtigForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        editable=True,
        verbose_name="Subject",
    )
    student = ext_models.PtigForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Student",
    )
    grade = models.FloatField(
        "Grade",
        null=True,
        blank=True,
        editable=True,
    )
    time = models.DateTimeField(
        "Time",
        null=True,
        blank=True,
        editable=True,
    )


admin_register(Grade)


class Lesson(models.Model):

    class Meta:
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

    parent = ext_models.PtigForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Subject",
    )
    teachers = ext_models.PtigManyToManyField(
        Teacher, editable=True, verbose_name="Teachers", related_name="lesson_teachers"
    )
    time_from = models.TimeField(
        "Time from",
        null=True,
        blank=True,
        editable=True,
    )
    time_to = models.TimeField(
        "Time to",
        null=True,
        blank=True,
        editable=True,
    )
    students = ext_models.PtigManyToManyField(
        Student, editable=True, verbose_name="Students", related_name="lesson_students"
    )


admin_register(Lesson)


class OGroup(schelements.models.Element):

    class Meta:
        verbose_name = _("Owner group")
        verbose_name_plural = _("Owner groups")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

        proxy = True

    @classmethod
    def table_action(cls, list_view, request, data):
        if "action" in data:
            print("X1", data)
            if data["action"] == "insert_rows":
                print("X2")
                return schjson.json_dumps({"OK": True})
        return standard_table_action(cls, list_view, request, data, ["copy", "paste"])


admin_register(OGroup)


class IGroup(schelements.models.Element):

    class Meta:
        verbose_name = _("Item group")
        verbose_name_plural = _("Item groups")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

        proxy = True


admin_register(IGroup)


class IGroupDevice(schelements.models.Element):

    class Meta:
        verbose_name = _("Group of devices")
        verbose_name_plural = _("Groups of devices")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

        proxy = True


admin_register(IGroupDevice)


class CGroup(schelements.models.Element):

    class Meta:
        verbose_name = _("Config group")
        verbose_name_plural = _("Config groups")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

        proxy = True


admin_register(CGroup)


class Administrator(schmasterdata.models.StandardEmployee):

    class Meta:
        verbose_name = _("Administrator")
        verbose_name_plural = _("Administrators")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

    email = models.EmailField(
        "Email",
        null=False,
        blank=False,
        editable=True,
        unique=True,
    )

    def save(self, *argi, **argv):
        print("SAVE__STUDENT!")
        super().save(*argi, **argv)

        x = self.name.split(" ", 1)
        if len(x) > 1:
            name = x[0]
            surname = x[1]
        else:
            name = ""
            surname = x
        # add_user(self, surname, name, self.email.lower(), 'ADMINISTRATOR')


admin_register(Administrator)


class LessonDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

    date_from = models.DateTimeField(
        "Date from",
        null=False,
        blank=False,
        editable=True,
    )
    date_to = models.DateTimeField(
        "Date to",
        null=False,
        blank=False,
        editable=True,
    )
    teacher = ext_models.PtigForeignKey(
        schelements.models.Element,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        editable=True,
        verbose_name="Teacher",
        limit_choices_to=get_teachers,
    )

    def __init__(self, *argi, **argv):
        super().__init__(*argi, **argv)
        [f for f in self._meta.fields if f.name == "number"][0].editable = False

    def save(self, *argi, **argv):
        self.date = self.date_from.date()
        return super().save(*argi, **argv)

    @classmethod
    def table_action(cls, list_view, request, data):
        if "action" in data:
            if data["action"] == "calendar_events":

                def all_day(date1, date2):
                    if (
                        date1
                        == datetime.datetime.combine(date1.date(), datetime.time.min)
                        and date1 + datetime.timedelta(1) == date2
                    ):
                        return True
                    else:
                        return False

                queryset = list_view.get_queryset()
                if "date" in data:
                    queryset = queryset.filter(
                        date=datetime.datetime.fromisoformat(data["date"])
                    )
                else:
                    if "start" in data:
                        queryset = queryset.filter(
                            date_from__gte=datetime.datetime.fromisoformat(
                                data["start"]
                            )
                        )
                    if "end" in data:
                        queryset = queryset.filter(
                            date_to__lte=datetime.datetime.fromisoformat(data["end"])
                        )

                return schjson.json_dumps(
                    [
                        {
                            "resourceId": obj.teacher.id,
                            "color": "#FE6B64",
                            "id": obj.pk,
                            "title": obj.number,
                            "start": obj.date_from.isoformat(),
                            "end": obj.date_to.isoformat(),
                            "allDay": all_day(obj.date_from, obj.date_to),
                        }
                        for obj in queryset
                        if obj.teacher
                    ]
                )
            if data["action"] == "calendar_change_event":
                pk = data["id"]
                date_from = data["start"]
                date_to = data["end"]
                teacher_id = int(data["resource_id"])
                teacher = schelements.models.Element.objects.get(id=teacher_id)
                tab = list_view.get_queryset().filter(pk=pk)
                if len(tab) > 0:
                    obj = tab[0]
                    if date_from:
                        obj.date_from = datetime.datetime.fromisoformat(date_from)
                    if date_to:
                        obj.date_to = datetime.datetime.fromisoformat(date_to)
                    obj.teacher = teacher
                    obj.save()
                    return {"OK": True}
        return None

    @classmethod
    def get_teachers(cls):
        return ";".join(
            [
                str(item.id) + ":" + item.name
                for item in schelements.models.Element.objects.filter(get_teachers())
            ]
        )


admin_register(LessonDocHead)


class LessonDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "school"

        ordering = ["id"]

        proxy = True

    if False:

        def __init__(self, *argi, **argv):
            super().__init__(*argi, **argv)
            field = self.set_field_value("item", "blank", False)
            field.verbose_name = _("Lesson type")
            field = self.set_field_value("owner", "blank", False)
            field.verbose_name = _("Student")

        def get_form_class(self, view, request, create):
            base_form = view.get_form_class()

            class _Form(base_form):
                def __init__(self, *args, **kwargs):
                    print("F1", args, kwargs)
                    super().__init__(*args, **kwargs)
                    print("F2", args, kwargs)
                    if self.instance.parent and self.instance.parent.id:
                        print("F3", args, kwargs)
                        students = schelements.models.Element.get_children_for_element(
                            self.instance.parent.parent_element.code, "O-CUS"
                        )
                        # products = schelements_models.Element.get_children_for_element('PR', 'I-PRD')
                        products = schelements.models.Element.get_children_for_element(
                            self.instance.parent.parent_element.code, "I-PRD"
                        )

                        self.fields["owner"].queryset = students
                        self.fields["item"].queryset = products
                        print("F4", args, kwargs)

            return _Form


admin_register(LessonDocItem)
