from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^YzKsApHu8H2/(?P<key>[\w-]+)/(?P<value>[\w-]+)/$", views.extra_accept, name="extra_accept"),
]
