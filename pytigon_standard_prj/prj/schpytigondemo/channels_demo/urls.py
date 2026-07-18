from django.urls import path
from pytigon_lib.schviews import generic_table_start
from . import views

urlpatterns = [
    path("clock/", views.clock, {}, name="channels_demo_clock"),
    path("ai/", views.openai, {}, name="channels_demo_openai"),
    path("ollamaai/", views.ollama_ai, {}, name="channels_demo_ollama_ai"),
]

gen = generic_table_start(urlpatterns, "channels_demo", views)
