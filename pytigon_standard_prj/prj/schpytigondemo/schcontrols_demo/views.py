from django import forms

from pytigon_lib.schviews.form_fun import form_with_perms

from django.utils.translation import gettext_lazy as _


PFORM = form_with_perms("schcontrols_demo")


class TestForm(forms.Form):
    test_field_1 = forms.CharField(
        label=_("Test field 1"),
        required=True,
    )
    test_field_2 = forms.BooleanField(
        label=_("Test field 2"),
        required=True,
    )
    test_field_3 = forms.DateField(
        label=_("Test field 3"),
        required=True,
    )
    test_field_4 = forms.EmailField(
        label=_("Test field 4"),
        required=False,
    )
    integer_field = forms.IntegerField(
        label=_("Integer field"),
        required=True,
    )
    float_field = forms.FloatField(
        label=_("FloatField"),
        required=True,
    )

    def process(self, request, queryset=None):

        object_list = [[1, 2, 3, 4, 5, 6, 7, 8] for _ in range(21)]

        return {"object_list": object_list}


def view_testform(request, *argi, **argv):
    return PFORM(request, TestForm, "schcontrols_demo/formtestform.html", {})
