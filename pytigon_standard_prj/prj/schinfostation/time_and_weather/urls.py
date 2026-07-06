from django.urls import path, re_path, include, reverse
from django.utils.translation import gettext_lazy as _
from pytigon_lib.schviews import generic_table_start, gen_tab_action, gen_row_action
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("home", views.home, {}, name="time_and_weather_home"),
    path("../", views.index, {}, name="time_and_weather_index"),
]

gen = generic_table_start(urlpatterns, "time_and_weather", views)
