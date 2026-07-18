from django.urls import path
from pytigon_lib.schviews import generic_table_start
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("svg/", TemplateView.as_view(template_name="components/svg.html"), {}),
]

gen = generic_table_start(urlpatterns, "components", views)
