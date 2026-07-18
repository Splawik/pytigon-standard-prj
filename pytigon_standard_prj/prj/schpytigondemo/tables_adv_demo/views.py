from django import forms

from pytigon_lib.schviews.form_fun import form_with_perms

from django.utils.translation import gettext_lazy as _


PFORM = form_with_perms("tables_adv_demo")


class _FilterFormAlbum(forms.Form):
    artist = forms.CharField(
        label=_("Artist"), required=False, max_length=None, min_length=None
    )

    def process(self, request, queryset=None):

        artist = self.cleaned_data["artist"]
        if artist:
            queryset = queryset.filter(artist__contains=artist)
        return queryset


def view__filterformalbum(request, *argi, **argv):
    return PFORM(
        request, _FilterFormAlbum, "tables_adv_demo/form_filterformalbum.html", {}
    )
