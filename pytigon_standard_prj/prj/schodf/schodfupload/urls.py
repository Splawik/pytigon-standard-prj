from django.urls import path
from pytigon_lib.schviews import generic_table_start
from . import views

urlpatterns = [
    path("odf_upload/", views.odf_upload, {}, name="schodfupload_odf_upload"),
    path("form/OdfUploadForm/", views.view_odfuploadform, {}),
]

gen = generic_table_start(urlpatterns, "schodfupload", views)
