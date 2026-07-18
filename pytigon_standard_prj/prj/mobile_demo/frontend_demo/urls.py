from django.urls import path
from pytigon_lib.schviews import generic_table_start
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path(
        "dynamic_fragment/",
        TemplateView.as_view(template_name="frontend_demo/dynamic_fragment.html"),
        {},
    ),
]

gen = generic_table_start(urlpatterns, "frontend_demo", views)
