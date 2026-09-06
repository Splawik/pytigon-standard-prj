from django.urls import path, re_path
from django.views.generic import TemplateView
from pytigon_lib.schviews import generic_table_start

from . import views

urlpatterns = [
    path("excel/", views.excel_report, {}, name="templates_demo_excel_report"),
    path("odf/", views.odf_report, {}, name="templates_demo_odf_report"),
    re_path(
        r"example/(?P<param>[^/]*)/$", views.example, {}, name="templates_demo_example"
    ),
    path(
        "example_template/",
        TemplateView.as_view(template_name="templates_demo/example_template.html"),
        {},
    ),
    path(
        "min_template/",
        TemplateView.as_view(template_name="templates_demo/min_template.html"),
        {},
    ),
    path(
        "min_template2/",
        TemplateView.as_view(template_name="templates_demo/min_template2.html"),
        {},
    ),
    path(
        "target/", TemplateView.as_view(template_name="templates_demo/target.html"), {}
    ),
    path(
        "region/", TemplateView.as_view(template_name="templates_demo/region.html"), {}
    ),
    path("min/", TemplateView.as_view(template_name="templates_demo/min.html"), {}),
    path(
        "details/",
        TemplateView.as_view(template_name="templates_demo/details_window.html"),
        {},
    ),
]

gen = generic_table_start(urlpatterns, "templates_demo", views)
