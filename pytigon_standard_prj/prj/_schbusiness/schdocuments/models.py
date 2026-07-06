import os, os.path
import sys

import django
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import admin

from pytigon_lib.schdjangoext.fields import *
import pytigon_lib.schdjangoext.fields as ext_models
from pytigon_lib.schdjangoext.models import *
from pytigon_lib.schtools import schjson
from pytigon_lib.schhtml.htmltools import superstrip

import schelements.models


from django.db.models import Q, Sum

# Reception/Przyjęcie zewnętrzne: IR - Internal Receiving
# Production/Przyjęcie wewnętrzne: GR - Goods Received Note

# Issue/Wydanie zewnętrzne: CI - Stock Issue Confirmation
# Consumpction/Rozchód wewnętrzny: IC - Internal Consumption

# Transfer/Przesunięcie magazynowe: WT - warehouse transfer sheet
# Transformation/Transformacja: TR- warehouse transformation

# Order/Zamówienie: OR - Order
# Invoice/Faktura: IN - Invoice

# Price/Cennik: PL - Price list
# Agreement/Porozumienie handlowe: TB - Terms of Business

# Decree/Nota księgowa: AN - Accounting note

# Opening/Bilans otwarcia: OB - opening balance
# Closing/Bilans zamknięcia: CB - closing balance

# Purchase/Faktura zakupu: PIV - Purchase invoice
# PurchaseOrder/Zamówienie zakupu: PO - Purchase order
# Requirement/Zapotrzebowanie: PQ - Purchase Requirement

# Stocktaking/Inwentaryzacja: ST - Stocktaking


PaymentTypeChoice = [
    ("1", "E-payments"),
    ("2", "Prepayment - bank transfer"),
    ("3", "Credit Agreement"),
]


class OrderDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]

    payment_type = models.CharField(
        "Payment type",
        null=False,
        blank=False,
        editable=True,
        default="1",
        choices=PaymentTypeChoice,
        max_length=1,
    )
    delivery_date = models.DateField(
        "Delivery date",
        null=True,
        blank=True,
        editable=True,
    )


admin_register(OrderDocHead)


class OrderDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Order item")
        verbose_name_plural = _("Order items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]

    price = models.DecimalField(
        "Price", null=False, blank=False, editable=True, decimal_places=2, max_digits=12
    )
    gross_price = models.BooleanField(
        "Is this the gross price",
        null=False,
        blank=False,
        editable=True,
        default=False,
    )
    remaining_qty = models.DecimalField(
        "Remaining quantity",
        null=True,
        blank=True,
        editable=True,
        decimal_places=2,
        max_digits=12,
    )


admin_register(OrderDocItem)


class InvoiceDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(InvoiceDocHead)


class InvoiceDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Invoice item")
        verbose_name_plural = _("Invoice items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]

    amount_gross = models.DecimalField(
        "Gross amount",
        null=False,
        blank=False,
        editable=True,
        decimal_places=2,
        max_digits=12,
    )
    amount_net = models.DecimalField(
        "Net amount",
        null=False,
        blank=False,
        editable=True,
        decimal_places=2,
        max_digits=12,
    )
    currency = models.CharField(
        "Currency", null=True, blank=True, editable=True, max_length=16
    )
    vat_rate = models.CharField(
        "VAT rate", null=True, blank=True, editable=True, max_length=16
    )


admin_register(InvoiceDocItem)


class ReceptionDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Reception")
        verbose_name_plural = _("Receptions")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(ReceptionDocHead)


class ReceptionDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Reception item")
        verbose_name_plural = _("Reception items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(ReceptionDocItem)


class ProductionDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Production")
        verbose_name_plural = _("Productions")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(ProductionDocHead)


class ProductionDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Production item")
        verbose_name_plural = _("Production items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(ProductionDocItem)


class IssueDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Issue")
        verbose_name_plural = _("Issues")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(IssueDocHead)


class IssueDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Issue item")
        verbose_name_plural = _("Issue items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]

    account_state = ext_models.PtigForeignKey(
        schelements.models.AccountState,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Stock account state",
        limit_choices_to=Q(parent__name="@-qty")
        & Q(aggregate=False)
        & Q(zero_balance=False),
    )
    max_qty = models.DecimalField(
        "Maximum quantity",
        null=False,
        blank=False,
        editable=False,
        default=0,
        decimal_places=2,
        max_digits=12,
    )

    def copy_to(self, doc_item_dest):
        doc_item_dest.account_state = self.account_state
        doc_item_dest.max_qty = self.account_state.max_qty
        super().copy_to(doc_item_dest)


admin_register(IssueDocItem)


class ConsumpctionDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Consumpction")
        verbose_name_plural = _("Consumpctions")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(ConsumpctionDocHead)


class ConsumpctionDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Consumpction item")
        verbose_name_plural = _("Consumpction items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(ConsumpctionDocItem)


class TransferDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Transfer")
        verbose_name_plural = _("Transfers")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(TransferDocHead)


class TransferDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Transfer item")
        verbose_name_plural = _("Transfer items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(TransferDocItem)


class PriceDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(PriceDocHead)


class PriceDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Price item")
        verbose_name_plural = _("Price items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(PriceDocItem)


class AgreementDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Agreement")
        verbose_name_plural = _("Agreements")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(AgreementDocHead)


class AgreementDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Agreement item")
        verbose_name_plural = _("Agreement items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(AgreementDocItem)


class DecreeDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Decree")
        verbose_name_plural = _("Decrees")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(DecreeDocHead)


class DecreeDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Decree item")
        verbose_name_plural = _("Decree items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(DecreeDocItem)


class OpeningDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Opening")
        verbose_name_plural = _("Openings")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(OpeningDocHead)


class OpeningDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Opening item")
        verbose_name_plural = _("Opening items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(OpeningDocItem)


class ClosingDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Closing")
        verbose_name_plural = _("Closings")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(ClosingDocHead)


class ClosingDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Closing item")
        verbose_name_plural = _("Closing items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(ClosingDocItem)


class TransformationDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Transformation")
        verbose_name_plural = _("Transformations")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(TransformationDocHead)


class TransformationDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Transformation item")
        verbose_name_plural = _("Transformation items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(TransformationDocItem)


class PurchaseDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Purchase")
        verbose_name_plural = _("Purchases")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(PurchaseDocHead)


class PurchaseDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Purchase item")
        verbose_name_plural = _("Purchase items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]

    amount_gross = models.DecimalField(
        "Gross amount",
        null=False,
        blank=False,
        editable=True,
        decimal_places=2,
        max_digits=12,
    )
    amount_net = models.DecimalField(
        "Net amount",
        null=True,
        blank=True,
        editable=True,
        decimal_places=2,
        max_digits=12,
    )
    currency = models.CharField(
        "Currency", null=True, blank=True, editable=True, max_length=16
    )
    vat_rate = models.CharField(
        "VAT rate", null=True, blank=True, editable=True, max_length=16
    )


admin_register(PurchaseDocItem)


class RequirementDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Requirement")
        verbose_name_plural = _("Requirements")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(RequirementDocHead)


class RequirementDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Requirement item")
        verbose_name_plural = _("Reguirement items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(RequirementDocItem)


class PurchaseOrderDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Purchase order")
        verbose_name_plural = _("Purchase orders")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(PurchaseOrderDocHead)


class PurchaseOrderDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Purchase order item")
        verbose_name_plural = _("Purchase order items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(PurchaseOrderDocItem)


class StocktakingDocHead(schelements.models.DocHead):

    class Meta:
        verbose_name = _("Stocktaking")
        verbose_name_plural = _("Stocktakings")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(StocktakingDocHead)


class StocktakingDocItem(schelements.models.DocItem):

    class Meta:
        verbose_name = _("Stocktaking item")
        verbose_name_plural = _("Stocktaking items")
        default_permissions = ("add", "change", "delete", "view", "list", "administer")
        app_label = "schdocuments"

        ordering = ["id"]


admin_register(StocktakingDocItem)
