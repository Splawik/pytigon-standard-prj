from django.urls import path
from pytigon_lib.schviews import generic_table_start
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path(
        "standardcontrols",
        TemplateView.as_view(template_name="schcontrols_demo/standard_controls.html"),
        {"title": "Standard controls"},
    ),
    path(
        "extendedcontrols",
        TemplateView.as_view(template_name="schcontrols_demo/extended_controls.html"),
        {},
    ),
    path("form/TestForm/", views.view_testform, {}),
]

gen = generic_table_start(urlpatterns, "schcontrols_demo", views)
