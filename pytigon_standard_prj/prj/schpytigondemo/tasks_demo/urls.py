from django.urls import path
from pytigon_lib.schviews import generic_table_start
from . import views

urlpatterns = [
    path("test_task/", views.test_task, {}, name="tasks_demo_test_task"),
    path("test_task2/", views.test_task2, {}, name="tasks_demo_test_task2"),
    path("test_messages", views.test_messages, {}, name="tasks_demo_test_messages"),
]

gen = generic_table_start(urlpatterns, "tasks_demo", views)
