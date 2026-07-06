from django.urls import path, re_path, include, reverse
from django.utils.translation import gettext_lazy as _
from pytigon_lib.schviews import generic_table_start, gen_tab_action, gen_row_action
from django.views.generic import TemplateView
from . import views

urlpatterns = []

gen = generic_table_start(urlpatterns, "schprice_lists", views)


gen.standard("RetailPrice", _("Retail price"), _("Retail price list"))
gen.standard("Price", _("Price"), _("Price list"))

gen.for_field(
    "schelements.Element",
    "sold_item_retail_prices",
    _("Retail price"),
    _("Retail price list"),
)
gen.for_field("schelements.Element", "sold_item_prices", _("Price"), _("Price list"))
gen.for_field("schelements.Element", "customer_prices", _("Price"), _("Price list"))
