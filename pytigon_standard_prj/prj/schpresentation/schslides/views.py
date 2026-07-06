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

from pytigon_lib.schviews.viewtools import change_pos, duplicate_row


@dict_to_template("schslides/v_generate.html")
def generate(request, pk):

    from pytigon_lib.schfs.vfstools import open_and_create_dir

    widgets = []
    steps = []
    to_hide = []

    show = models.Show.objects.get(pk=pk)

    dir_name = os.path.join(
        settings.MEDIA_ROOT, "slideshow", show.name.replace(" ", "_")
    )
    file_name = os.path.join(dir_name, "index.html")

    i = 1
    with open_and_create_dir(file_name, "wt") as index:
        for slide in show.slide_set.all():
            ext = slide.file.name.split(".")[-1].lower()
            print("X1:", ext)
            s = ""
            if ext in ("jpeg", "jpg", "png", "gif"):
                s = f"<img id='s{i}' class='slideobj obj{i}' src='{slide.file.url}' />"
            if ext == "svg":
                s = f"<svg id='s{i}' class='slideobj obj{i}' src='{slide.file.url}' />"
            if ext == "mp4":
                s = f"<video id='s{i}' class='slideobj obj{i}' src='{slide.file.url}' muted='muted' />"
            if ext == "html":
                s = f"<iframe id='s{i}' class='slideobj obj{i}' src='{slide.file.url}' />"
            if ext == "md":
                s = f"<iframe id='s{i}' class='slideobj obj{i}' src='{slide.file.url}' />"
            if s:
                for pos in to_hide:
                    pos[0] -= 1
                widgets.append(s)
                steps.append(
                    (
                        "show",
                        f"s{i}",
                    )
                )
                if slide.time:
                    t = int(slide.time * 1000)
                else:
                    t = 10000
                steps.append(
                    (
                        "sleep",
                        t,
                    )
                )
                if slide.end_effect_shift:
                    if slide.end_effect_shift > 0:
                        to_hide.append([slide.end_effect_shift, f"s{i}"])
                else:
                    steps.append(
                        (
                            "hide",
                            f"s{i}",
                        )
                    )

                for pos in to_hide:
                    if pos[0] == 0:
                        steps.append(
                            (
                                "hide",
                                pos[1],
                            )
                        )

                i += 1

        for pos in to_hide:
            if pos[0] > 0:
                steps.append(
                    (
                        "hide",
                        pos[1],
                    )
                )

        context = {
            "widgets": widgets,
            "steps": steps,
        }
        index.write(
            render_to_string("schslides/slideshow_template.html", context, request)
        )

    return {"object_list": show.slide_set.all()}
