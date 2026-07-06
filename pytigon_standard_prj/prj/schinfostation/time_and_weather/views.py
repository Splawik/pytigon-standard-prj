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

import requests, json


@dict_to_template("time_and_weather/v_home.html")
def home(request, **argv):

    api_key = "479d27874a5c2cf7fc7c73ba79387e4c"
    base_url = "http://api.openweathermap.org/data/2.5/onecall?"
    city_name = "Kozienice"
    complete_url = (
        base_url
        + "appid="
        + api_key
        + "&lat=51.610044&lon=21.491410&units=metric&lang=pl"
    )
    response = requests.get(complete_url)
    x = response.json()
    return x


@dict_to_template("time_and_weather/v_index.html")
def index(request, **argv):

    return {}
