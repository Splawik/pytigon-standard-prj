from django.urls import path
from pytigon_lib.schviews import generic_table_start
from . import views

urlpatterns = [
    path(
        "test_interfaces/", views.test_interfaces, {}, name="interfaces_test_interfaces"
    ),
]

gen = generic_table_start(urlpatterns, "interfaces", views)
