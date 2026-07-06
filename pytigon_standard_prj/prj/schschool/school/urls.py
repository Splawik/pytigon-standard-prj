from django.urls import path, re_path, include, reverse
from django.utils.translation import gettext_lazy as _
from pytigon_lib.schviews import generic_table_start, gen_tab_action, gen_row_action
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    gen_row_action("Class", "class_view", views.class_view),
    path(
        "statistic_for_user/", views.statistict_user, {}, name="school_statistict_user"
    ),
    path(
        "statistic_for_teacher/",
        views.statistic_teacher,
        {},
        name="school_statistic_teacher",
    ),
    path("email", TemplateView.as_view(template_name="school/email_template.html"), {}),
]

gen = generic_table_start(urlpatterns, "school", views)
gen.for_field("LessonDocHead", "docitem_set", _("Lesson"), _("Lessons"))
gen.for_field("LessonDocHead", "docitem_set", _("Lesson"), _("Lessons"))


gen.standard("Class", _("Class"), _("Classes"))
gen.standard("SubjectType", _("Subject type"), _("Subject types"))
gen.standard("Subject", _("Subject"), _("Subjects"))
gen.standard("Teacher", _("Teacher"), _("Teachers"))
gen.standard("School", _("School"), _("Schools"))
gen.standard("Student", _("Student"), _("Students"))
gen.standard("Grade", _("Grade"), _("Grades"))
gen.standard("Lesson", _("Lesson"), _("Lessons"))
gen.standard("OGroup", _("Owner group"), _("Owner groups"))
gen.standard("IGroup", _("Item group"), _("Item groups"))
gen.standard("IGroupDevice", _("Group of devices"), _("Groups of devices"))
gen.standard("CGroup", _("Config group"), _("Config groups"))
gen.standard("Administrator", _("Administrator"), _("Administrators"))
gen.standard("LessonDocHead", _("Lesson"), _("Lessons"))
gen.standard("LessonDocItem", _("Lesson"), _("Lessons"))

gen.for_field("Class", "subject_set", _("Subject"), _("Subjects"))
gen.for_field("SubjectType", "subject_set", _("Subject"), _("Subjects"))
gen.for_field("Subject", "teacher_subjects", _("Teacher"), _("Teachers"))
gen.for_field("Subject", "grade_set", _("Grade"), _("Grades"))
gen.for_field("Student", "grade_set", _("Grade"), _("Grades"))
gen.for_field("Subject", "lesson_set", _("Lesson"), _("Lessons"))
gen.for_field("Teacher", "lesson_teachers", _("Lesson"), _("Lessons"))
gen.for_field("Student", "lesson_students", _("Lesson"), _("Lessons"))
gen.for_field("schelements.Element", "lessondochead_set", _("Lesson"), _("Lessons"))
