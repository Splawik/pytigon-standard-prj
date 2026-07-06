from django.urls import path, re_path, include, reverse
from django.utils.translation import gettext_lazy as _
from pytigon_lib.schviews import generic_table_start, gen_tab_action, gen_row_action
from django.views.generic import TemplateView
from . import views

urlpatterns = []

gen = generic_table_start(urlpatterns, "schmasterdata", views)


gen.standard(
    "UnitOfMeasure4Product",
    _("Unit of measure for the product"),
    _("Units of measure for the product"),
)
gen.standard("Bank4Contractor", _("Bank for contractor"), _("Banks for contractors"))
gen.standard("Company", _("Company"), _("Companies"))
gen.standard("Customer", _("Customer"), _("Customers"))
gen.standard("Supplier", _("Supplier"), _("Suppliers"))
gen.standard("Product", _("Product"), _("Products"))
gen.standard("Merchandise", _("Merchandise"), _("Merchandises"))
gen.standard("UnitOfMeasure", _("Unit of measure"), _("Units of measure"))
gen.standard("Employee", _("Employee"), _("Workers"))
gen.standard("Person", _("Person"), _("Persons"))
gen.standard("Location", _("Location"), _("Locations"))

gen.for_field(
    "schelements.Element",
    "unitofmeasure4product_set2",
    _("Unit of measure for the product"),
    _("Units of measure for the product"),
)
gen.for_field(
    "schelements.Element",
    "unitofmeasure4product_set",
    _("Unit of measure for the product"),
    _("Units of measure for the product"),
)
gen.for_field(
    "schelements.Element",
    "bank4contractor_set",
    _("Bank for contractor"),
    _("Banks for contractors"),
)
