from django.urls import path, re_path, include, reverse
from django.utils.translation import gettext_lazy as _
from pytigon_lib.schviews import generic_table_start, gen_tab_action, gen_row_action
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("test/", views.test, {}, name="shop_test"),
]

gen = generic_table_start(urlpatterns, "shop", views)
import saleor.urls
from django.urls.resolvers import URLResolver
from django.urls import include, path


def process_main_urls(main_urlpatterns):
    for item in saleor.urls.urlpatterns:
        main_urlpatterns.append(item)

        # if type(item) == URLResolver:
        #    try:
        # print(type(item), item)
        # item.pattern._regex = "../" + item.pattern._regex
        # urlpatterns.append(item)
        #    except:
        # pass
        # else:
        # urlpatterns.append(item)
