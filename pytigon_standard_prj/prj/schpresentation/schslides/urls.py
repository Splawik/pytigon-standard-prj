from django.urls import path, re_path, include, reverse
from django.utils.translation import gettext_lazy as _
from pytigon_lib.schviews import generic_table_start, gen_tab_action, gen_row_action
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    gen_row_action("Show", "generate", views.generate),
    gen_row_action(
        "Slide",
        "field_up",
        views.change_pos,
        {"app": "schslides", "tab": "Slide", "forward": False, "field": "parent"},
    ),
    gen_row_action(
        "Slide",
        "field_down",
        views.change_pos,
        {"app": "schslides", "tab": "Slide", "forward": True, "field": "parent"},
    ),
]

gen = generic_table_start(urlpatterns, "schslides", views)


gen.standard("Show", _("Show"), _("Shows"))
gen.standard("Slide", _("Slide"), _("Slides"))

gen.for_field("Show", "slide_set", _("Slide"), _("Slides"))
