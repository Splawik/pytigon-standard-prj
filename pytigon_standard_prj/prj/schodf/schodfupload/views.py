from django import forms

from pytigon_lib.schviews.form_fun import form_with_perms

from django.utils.translation import gettext_lazy as _


from pytigon_lib.schfs.vfstools import get_temp_filename
from pytigon_lib.schdjangoext.spreadsheet_render import render_to_response_odf


class y(object):
    name = "Hello world!"


class x(object):
    stanowisko = y()


PFORM = form_with_perms("schodfupload")


class OdfUploadForm(forms.Form):
    odf_file = forms.FileField(
        label=_("Odf file"),
        required=True,
    )

    def process(self, request, queryset=None):

        return {"object": x()}

    def render_to_response(self, request, template, context_instance):
        odfdata = request.FILES["odf_file"]
        file_name = get_temp_filename("temp.ods")

        plik = open(file_name, "wb")
        plik.write(odfdata.read())
        plik.close()

        return render_to_response_odf(file_name, context_instance=context_instance)


def view_odfuploadform(request, *argi, **argv):
    return PFORM(request, OdfUploadForm, "schodfupload/formodfuploadform.html", {})


def odf_upload(request, *args, **argv):

    return PFORM(request, OdfUploadForm, "schodfupload/odf_upload.html", {})
