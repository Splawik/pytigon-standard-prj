from pytigon_lib.schviews import generic_table_start
from . import views

urlpatterns = []

gen = generic_table_start(urlpatterns, "wiki_demo", views)
