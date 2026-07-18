from django import forms

from pytigon_lib.schviews.form_fun import form_with_perms

from django.utils.translation import gettext_lazy as _

from . import models


from pytigon_lib.schfs.vfstools import get_temp_filename
from pytigon_lib.schtools.install import Ptig


PFORM = form_with_perms("schinstall")


class upload_ptig(forms.Form):
    status = forms.CharField(
        label=_("Status"), required=False, max_length=None, min_length=None
    )
    ptig = forms.FileField(
        label=_("Pytigon install file (*.ptig)"),
        required=False,
        widget=forms.ClearableFileInput(attrs={"accept": ".ptig"}),
    )
    accept_license = forms.BooleanField(
        label=_("Accept license"),
        required=False,
        initial=False,
    )

    def process(self, request, queryset=None):

        status = self.cleaned_data["status"]
        if status:
            if status == "1":
                if "INSTALL_FILE_NAME" in request.session:
                    file_name = request.session["INSTALL_FILE_NAME"]
                    with Ptig(file_name) as ptig:
                        if ptig.is_ok():
                            accept_license = self.cleaned_data["accept_license"]
                            if accept_license:
                                object_list = ptig.extract_ptig()
                                ret = {"object_list": object_list, "status": 2}
                            else:
                                readmedata = archive.read(prj_name + "/README.md")
                                licensedata = archive.read(prj_name + "/LICENSE")
                                ret = {
                                    "object_list": None,
                                    "status": 1,
                                    "readmedata": ptig.get_readme(),
                                    "licensedata": ptig.get_license(),
                                    "first": False,
                                }
                        else:
                            ret = {"object_list": None, "status": None}
                    return ret
        else:
            if "ptig" in request.FILES:
                ptig_file = request.FILES["ptig"]
                file_name = get_temp_filename("temp.ptig")
                request.session["INSTALL_FILE_NAME"] = file_name
                with open(file_name, "wb") as f:
                    f.write(ptig_file.read())

                ret = {"object_list": None, "status": None}

                with Ptig(file_name) as ptig:
                    if ptig.is_ok():
                        self.initial = {
                            "accept_license": False,
                        }
                        ret = {
                            "object_list": None,
                            "status": 1,
                            "readmedata": ptig.get_readme(),
                            "licensedata": ptig.get_license(),
                            "first": True,
                        }
                return ret

        return {"object_list": None, "status": None}

    def clean(self):
        status = self.cleaned_data["status"]
        if not status:
            ret = {"status": None}
        else:
            if not self.cleaned_data["accept_license"]:
                self._errors["accept_license"] = ["The license must be approved"]
            ret = self.cleaned_data
        return ret

    def process_invalid(self, request, param=None):
        return {"object_list": []}


def view_upload_ptig(request, *argi, **argv):
    return PFORM(request, upload_ptig, "schinstall/formupload_ptig.html", {})


class download_ptig(forms.Form):
    project = forms.ChoiceField(
        label=_("Project"), required=True, choices=models.get_projects
    )
    export_db = forms.NullBooleanField(
        label=_("Export database"),
        required=True,
    )
    export_prj_source = forms.NullBooleanField(
        label=_("Export project source"),
        required=True,
    )


def view_download_ptig(request, *argi, **argv):
    return PFORM(request, download_ptig, "schinstall/formdownload_ptig.html", {})
