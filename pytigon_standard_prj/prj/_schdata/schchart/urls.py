from django.urls import re_path
from django.utils.translation import gettext_lazy as _
from pytigon_lib.schviews import generic_table_start
from . import views

urlpatterns = [
    re_path(
        r"plot_service/(?P<name>\w+)/$",
        views.plot_service,
        {},
        name="schchart_plot_service",
    ),
]

gen = generic_table_start(urlpatterns, "schchart", views)


gen.standard("Plot", _("Plot"), _("Plots"))
