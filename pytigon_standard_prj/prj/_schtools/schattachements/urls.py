from django.utils.translation import gettext_lazy as _
from pytigon_lib.schviews import gen_row_action, generic_table_start

from . import views

urlpatterns = [
    gen_row_action("Attachement", "download", views.download),
]

gen = generic_table_start(urlpatterns, "schattachements", views)


gen.standard("Attachement", _("Attachement"), _("Attachements"))

gen.for_field(
    "schelements.Element", "attachement_set", _("Attachement"), _("Attachements")
)
