from django.utils.translation import gettext_lazy as _
from pytigon_lib.schviews import generic_table_start
from . import views

urlpatterns = []

gen = generic_table_start(urlpatterns, "db_demo", views)


gen.standard("Teest", _("Test"), _("Tests"))
