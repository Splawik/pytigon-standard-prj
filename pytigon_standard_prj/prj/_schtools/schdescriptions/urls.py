from django.utils.translation import gettext_lazy as _
from pytigon_lib.schviews import generic_table_start
from . import views

urlpatterns = []

gen = generic_table_start(urlpatterns, "schdescriptions", views)


gen.standard("Description", _("Description"), _("Descriptions"))
