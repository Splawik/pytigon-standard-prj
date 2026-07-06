from django.urls import path, re_path, include, reverse
from django.utils.translation import gettext_lazy as _
from pytigon_lib.schviews import generic_table_start, gen_tab_action, gen_row_action
from django.views.generic import TemplateView
from . import views

urlpatterns = []

gen = generic_table_start(urlpatterns, "schdocuments", views)


gen.standard("OrderDocHead", _("Order"), _("Orders"))
gen.standard("OrderDocItem", _("Order item"), _("Order items"))
gen.standard("InvoiceDocHead", _("Invoice"), _("Invoices"))
gen.standard("InvoiceDocItem", _("Invoice item"), _("Invoice items"))
gen.standard("ReceptionDocHead", _("Reception"), _("Receptions"))
gen.standard("ReceptionDocItem", _("Reception item"), _("Reception items"))
gen.standard("ProductionDocHead", _("Production"), _("Productions"))
gen.standard("ProductionDocItem", _("Production item"), _("Production items"))
gen.standard("IssueDocHead", _("Issue"), _("Issues"))
gen.standard("IssueDocItem", _("Issue item"), _("Issue items"))
gen.standard("ConsumpctionDocHead", _("Consumpction"), _("Consumpctions"))
gen.standard("ConsumpctionDocItem", _("Consumpction item"), _("Consumpction items"))
gen.standard("TransferDocHead", _("Transfer"), _("Transfers"))
gen.standard("TransferDocItem", _("Transfer item"), _("Transfer items"))
gen.standard("PriceDocHead", _("Price"), _("Prices"))
gen.standard("PriceDocItem", _("Price item"), _("Price items"))
gen.standard("AgreementDocHead", _("Agreement"), _("Agreements"))
gen.standard("AgreementDocItem", _("Agreement item"), _("Agreement items"))
gen.standard("DecreeDocHead", _("Decree"), _("Decrees"))
gen.standard("DecreeDocItem", _("Decree item"), _("Decree items"))
gen.standard("OpeningDocHead", _("Opening"), _("Openings"))
gen.standard("OpeningDocItem", _("Opening item"), _("Opening items"))
gen.standard("ClosingDocHead", _("Closing"), _("Closings"))
gen.standard("ClosingDocItem", _("Closing item"), _("Closing items"))
gen.standard("TransformationDocHead", _("Transformation"), _("Transformations"))
gen.standard(
    "TransformationDocItem", _("Transformation item"), _("Transformation items")
)
gen.standard("PurchaseDocHead", _("Purchase"), _("Purchases"))
gen.standard("PurchaseDocItem", _("Purchase item"), _("Purchase items"))
gen.standard("RequirementDocHead", _("Requirement"), _("Requirements"))
gen.standard("RequirementDocItem", _("Requirement item"), _("Reguirement items"))
gen.standard("PurchaseOrderDocHead", _("Purchase order"), _("Purchase orders"))
gen.standard(
    "PurchaseOrderDocItem", _("Purchase order item"), _("Purchase order items")
)
gen.standard("StocktakingDocHead", _("Stocktaking"), _("Stocktakings"))
gen.standard("StocktakingDocItem", _("Stocktaking item"), _("Stocktaking items"))

gen.for_field(
    "schelements.AccountState", "issuedocitem_set", _("Issue item"), _("Issue items")
)
