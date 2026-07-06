from django.urls import path, re_path, include, reverse
from django.utils.translation import gettext_lazy as _
from pytigon_lib.schviews import generic_table_start, gen_tab_action, gen_row_action
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path(
        "get_shopping_cart_items_count",
        views.get_shopping_cart_items_count,
        {},
        name="schshop_get_shopping_cart_items_count",
    ),
    path("create_order", views.create_order, {}, name="schshop_create_order"),
    path(
        "payment_details/<int:payment_id>/",
        views.payment_details,
        {},
        name="schshop_payment_details",
    ),
    path(
        "payment_info/<int:payment_id>/<str:status>/",
        views.payment_info,
        {},
        name="schshop_payment_info",
    ),
    path("form/PurchasingItemForm/", views.view_purchasingitemform, {}),
]

gen = generic_table_start(urlpatterns, "schshop", views)


gen.standard("ShopGood", _("Shop good"), _("Shop goods"))
gen.standard("ShoppingCart", _("Shopping cart"), _("Shopping cart"))
gen.standard("Payment", _("Payment"), _("Payments"))

gen.for_field(
    "ShopGood", "shoppingcart_product_set", _("Shopping cart"), _("Shopping cart")
)
gen.for_field(
    "schprofile.UserProxy", "shoppingcart_set", _("Shopping cart"), _("Shopping cart")
)
gen.for_field(
    "schelements.Element",
    "shoppingcart_customer_set",
    _("Shopping cart"),
    _("Shopping cart"),
)
gen.for_field("schelements.DocHead", "payment_set", _("Payment"), _("Payments"))
urlpatterns.append(path("../payments/", include("payments.urls")))
