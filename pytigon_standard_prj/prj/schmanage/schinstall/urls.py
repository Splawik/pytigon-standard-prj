from django.urls import path
from pytigon_lib.schviews import generic_table_start
from . import views

urlpatterns = [
    path("form/upload_ptig/", views.view_upload_ptig, {}),
    path("form/download_ptig/", views.view_download_ptig, {}),
]

gen = generic_table_start(urlpatterns, "schinstall", views)
