from django.utils.translation import gettext_lazy as _

import os
import sys
import datetime
import time
from queue import Empty
from pytigon_lib.schtasks.publish import publish


from django.contrib.auth import get_user_model
from webpush import send_group_notification, send_user_notification


def test_group_webpush(cproxy=None, **kwargs):

    payload = {"head": "Welcome!", "body": "Hello World clock"}
    send_group_notification(group_name="auto", payload=payload, ttl=1000)


def test_user_webpush(cproxy=None, **kwargs):

    object_list = get_user_model().objects.filter(username="auto")
    user = object_list[0]

    payload = {"head": "Welcome!", "body": "Hello World"}

    send_user_notification(user=user, payload=payload, ttl=1000)

    payload = {
        "head": "Welcome!",
        "body": "Hello world!",
        "icon": "https://i.imgur.com/dRDxiCQ.png",
        "url": "https://www.example.com",
    }

    send_user_notification(user=user, payload=payload, ttl=1000)
