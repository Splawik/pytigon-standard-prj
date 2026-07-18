from django.utils.translation import gettext_lazy as _
from pytigon_lib.schviews import generic_table_start, gen_row_action
from . import views

urlpatterns = [
    gen_row_action("Attachment", "download", views.download),
]

gen = generic_table_start(urlpatterns, "schattachments", views)


gen.standard("Attachment", _("Attachment"), _("Attachments"))

gen.for_field(
    "schelements.Element", "attachment_set", _("Attachment"), _("Attachments")
)
