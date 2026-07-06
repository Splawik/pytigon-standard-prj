from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, reverse
from django import forms
from django.template.loader import render_to_string
from django.template import Context, Template
from django.template import RequestContext
from django.conf import settings
from django.views.generic import TemplateView

from pytigon_lib.schviews.form_fun import form_with_perms
from pytigon_lib.schviews.viewtools import (
    dict_to_template,
    dict_to_odf,
    dict_to_pdf,
    dict_to_json,
    dict_to_xml,
    dict_to_ooxml,
    dict_to_txt,
    dict_to_hdoc,
)
from pytigon_lib.schviews.viewtools import render_to_response
from pytigon_lib.schdjangoext.tools import make_href
from pytigon_lib.schdjangoext import formfields as ext_form_fields
from pytigon_lib.schviews import actions

from django.utils.translation import gettext_lazy as _

from . import models
import os
import sys
import datetime
from django.utils import timezone

from schelements.models import Element, DocType, DocHead, DocItem
from schdocuments.models import OrderDocHead, OrderDocItem
from django.http import Http404
from django.db.models import Q, Sum

from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from payments import get_payment_model, RedirectNeeded

PRODUCTS_QUERYSET = Element.objects.filter(
    Q(type__startswith="I-PRD") | Q(type__startswith="I-MER")
)


PFORM = form_with_perms("schshop")


class PurchasingItemForm(forms.Form):
    product = ext_form_fields.ModelSelect2Field(
        label=_("Product variant"),
        required=True,
        queryset=PRODUCTS_QUERYSET,
        search_fields=[
            "name__icontains",
        ],
    )
    qty = forms.DecimalField(
        label=_("Quantity"),
        required=True,
        max_value=None,
        min_value=0,
        max_digits=12,
        decimal_places=2,
    )

    def process(self, request, queryset=None):

        print("A0:", request.GET)
        cart = models.ShoppingCart()
        cart.product = self.cleaned_data["product"]
        print("A1:", cart.product)
        cart.qty = self.cleaned_data["qty"]
        print("A2:", cart.qty)
        cart.user = request.user
        cart.customer = request.user.profile.owner
        print("A3:", request.user.profile.owner)
        cart.save()
        print("A4:")
        return actions.cancel(request)

    @classmethod
    def get_form_arguments(cls, request):
        pk = request.GET.get("pk")
        if pk:
            return {"initial": {"product": int(pk), "qty": 1}}
        else:
            return None


def view_purchasingitemform(request, *argi, **argv):
    return PFORM(request, PurchasingItemForm, "schshop/formpurchasingitemform.html", {})


def get_shopping_cart_items_count(request, **argv):

    count = models.ShoppingCart.objects.all().count()
    if count > 0:
        return HttpResponse(
            "<i class='fa fa-shopping-cart fa-lg'></i><span class='badge rounded-pill text-bg-danger'>%d</span>"
            % count
        )
    else:
        return HttpResponse("")


def create_order(request, **argv):

    doc_type = DocType.objects.filter(name="SO")
    if len(doc_type) == 1:
        object_list = models.ShoppingCart.objects.filter(user=request.user)
        if object_list.count() > 0:
            doc = OrderDocHead()
            if request.user.profile.owner:
                doc.parent_element = request.user.profile.owner
            doc.doc_type_parent = doc_type[0]
            doc.date = timezone.now()
            doc.status = "draft"
            doc.operator = request.user.username
            doc.save()
            i = 1
            for object in object_list:
                print(object, type(object), dir(object))
                item = OrderDocItem()
                item.parent = doc
                item.order = i
                item.item = object.product
                item.qty = object.qty
                item.active = True

                item.price = object.product.sold_item_prices.aggregate(
                    price=Sum("price")
                )["price"]
                if not item.price:
                    item.price = object.product.sold_item_retail_prices.all().aggregate(
                        retail_price=Sum("retail_price")
                    )["retail_price"]

                item.save()

                i += 1
            object_list.delete()
            return HttpResponse(
                "/schelements/table/DocHead/Order/form/list/?view_in=desktop&only_content|/schelements/table/DocHead/%d/edit/|inline_info|button.ladda-button"
                % doc.id,
                headers={
                    "Content-Disposition": "redirect",
                },
            )

    return Http404("Document type SO doesn't exists")


def payment_details(request, payment_id):

    payment = get_object_or_404(get_payment_model(), id=payment_id)

    try:
        form = payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))

    return TemplateResponse(
        request, "schshop/payment_form.html", {"form": form, "payment": payment}
    )


@dict_to_template("schshop/v_payment_info.html")
def payment_info(request, payment_id, status):

    payment = get_object_or_404(get_payment_model(), id=payment_id)
    return {"payment": payment, "status": status}
