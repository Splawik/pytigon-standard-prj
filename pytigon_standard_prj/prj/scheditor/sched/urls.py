from django.urls import path
from pytigon_lib.schviews import generic_table_start
from . import views

urlpatterns = [
    path("save/$", views.save, {}, name="sched_save"),
]

gen = generic_table_start(urlpatterns, "sched", views)
