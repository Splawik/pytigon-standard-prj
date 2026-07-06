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


def getstarttime():
    return datetime.datetime.now() + datetime.timedelta(minutes=-15)


def getendtime():
    return datetime.datetime.now() + datetime.timedelta(hours=3)


PFORM = form_with_perms("epg")


class _FilterFormEpg(forms.Form):
    time_from = forms.DateTimeField(
        label=_("Time from"),
        required=False,
        initial=getstarttime,
    )
    time_to = forms.DateTimeField(
        label=_("Time to"),
        required=False,
        initial=getendtime,
    )
    channel = forms.CharField(
        label=_("Channel"), required=False, max_length=None, min_length=None
    )
    category = forms.CharField(
        label=_("Category"), required=False, max_length=None, min_length=None
    )
    rating = forms.IntegerField(
        label=_("Rating"), required=False, initial=60, max_value=100, min_value=0
    )

    def process(self, request, queryset=None):

        time_from = self.cleaned_data["time_from"]
        time_to = self.cleaned_data["time_to"]
        channel = self.cleaned_data["channel"]
        category = self.cleaned_data["category"]
        rating = self.cleaned_data["rating"]

        if time_from:
            queryset = queryset.filter(date_from__gte=time_from)
        if time_to:
            queryset = queryset.filter(date_from__lte=time_to)
        if channel:
            queryset = queryset.filter(channel__icontains=channel)
        if category:
            queryset = queryset.filter(category__icontains=channel)
        if rating:
            queryset = queryset.filter(rating__gte=rating)

        return queryset

    def process_empty_or_invalid(self, request, queryset):
        time_from = getstarttime()
        time_to = getendtime()
        rating = 60

        if time_from:
            queryset = queryset.filter(date_from__gte=time_from)
        if time_to:
            queryset = queryset.filter(date_to__lte=time_to)
        if rating:
            queryset = queryset.filter(rating__gte=rating)

        return queryset


def view__filterformepg(request, *argi, **argv):
    return PFORM(request, _FilterFormEpg, "epg/form_filterformepg.html", {})
