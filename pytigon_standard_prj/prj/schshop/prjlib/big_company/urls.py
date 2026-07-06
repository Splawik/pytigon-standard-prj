from django.conf.urls import url

from . import views
from . import queryset_proxy

urlpatterns = [
    url(r'find_profile/$',
        views.find_profile, name='find_profile'),
    url(r'set_profile/$',
        views.set_profile, name='set_profile'),
    url(r"^invite/(?P<uid>\d+)/$", views.invite, name="invite"),
]
