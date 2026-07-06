from django.urls import path, re_path, include, reverse
from django.utils.translation import gettext_lazy as _
from pytigon_lib.schviews import generic_table_start, gen_tab_action, gen_row_action
from django.views.generic import TemplateView
from . import views

urlpatterns = []

gen = generic_table_start(urlpatterns, "schhardware", views)


gen.standard("Device", _("Device"), _("Device"))
gen.standard("Computer", _("Computer"), _("Computers"))
gen.standard("Monitor", _("Monitor"), _("Monitors"))
gen.standard("Printer", _("Printer"), _("Printers"))
gen.standard("Phone", _("Phone"), _("Phones"))
gen.standard("OtherDevice", _("OtherDevice"), _("OtherDevices"))
