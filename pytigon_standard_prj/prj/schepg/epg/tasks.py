from django.utils.translation import gettext_lazy as _

import os
import sys
import datetime
import time
from queue import Empty
from pytigon_lib.schtasks.publish import publish


import httpx
import asyncio
import arrow
from html.parser import HTMLParser
from django.db import transaction


import logging

logger = logging.getLogger("pytigon_task")

from . import models


class AParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for item in attrs:
                if item[0] == "href" and item[1].startswith("https://bit.ly"):
                    self.links.append(item[1])


class ProgrammeParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = []
        self.item = None
        self.in_tag = None

    def handle_starttag(self, tag, attrs):
        if tag == "programme":
            if self.item:
                self.data.append(self.item)
            self.item = {}
            for pos in attrs:
                if pos[0] in ("start", "stop", "channel"):
                    self.item[pos[0]] = pos[1]
        elif tag in ("title", "star-rating", "desc", "date", "category", "country"):
            self.in_tag = tag

    def handle_endtag(self, tag):
        if tag in ("title", "star-rating", "desc", "date", "category", "country"):
            self.in_tag = None

    def handle_data(self, data):
        if self.in_tag:
            if self.in_tag in self.item:
                self.item[self.in_tag] += "; " + data
            else:
                self.item[self.in_tag] = data


async def _epg():
    async with httpx.AsyncClient() as client:
        # http://epg.listam3u.com
        # https://epg.ovh/pl.xml
        # r = await client.get(
        #    "https://epg.ovh/pl.xml"
        # )
        # parser = AParser()
        # parser.feed(r.text)
        # if len(parser.links) > 0:
        r = await client.get("https://epg.ovh/pl.xml")
        parser2 = ProgrammeParser()
        parser2.feed(r.text)
        return parser2.data
        # return None


async def test(cmd):
    print("TASK test")
    logger.exception(f"TASK test exception")


def init_schedule(scheduler, cmd, http):
    scheduler.add_task("in_minute_intervals()", test, cmd=cmd)


def epg_load(cproxy=None, **kwargs):

    ret = asyncio.run(_epg())
    if ret:
        blocked_channels = []
        blocked_categories = []

        object_list = models.BlockEpg.objects.all()
        for obj in object_list:
            if obj.element == "c":
                blocked_channels.append(obj.pattern)
            elif obj.element == "g":
                blocked_categories.append(obj.pattern)

        with transaction.atomic():
            models.Epg.objects.all().delete()
            i = 0
            for pos in ret:
                i += 1
                obj = models.Epg()
                obj.channel = pos["channel"][:64]
                # x = pos['start']
                # d1 = x[:4]+"-"+x[4:6]+"-"+x[6:8] + " " + x[8:10]+":"+x[10:12]
                # x = pos['stop']
                # d2 = x[:4]+"-"+x[4:6]+"-"+x[6:8] + " " + x[8:10]+":"+x[10:12]
                # obj.date_from = d1
                # obj.date_to = d2
                obj.date_from = arrow.get(pos["start"], "YYYYMMDDHHmmss Z").datetime
                obj.date_to = arrow.get(pos["stop"], "YYYYMMDDHHmmss Z").datetime
                obj.title = pos["title"]
                obj.description = pos.get("desc", "")
                r = (
                    pos.get("star-rating", "0")
                    .replace(";", "")
                    .replace("\r", "")
                    .replace("\n", "")
                    .strip()
                )

                try:
                    if r == "10/10":
                        r2 = 100
                    else:
                        r2 = eval(r)
                        if r2 < 1:
                            r2 = int(r2 * 100)
                except Exception as e:
                    print("star-rating:", r)
                    print(str(e))
                    r2 = 0

                obj.rating = r2
                obj.category = pos.get("category", "")[:64]
                obj.country = pos.get("country", "")[:64]
                y = pos.get("date", "0")
                y2 = int(y)
                obj.year = y2

                test = True

                for pos in blocked_channels:
                    if pos in obj.channel:
                        test = False
                        break

                if test:
                    for pos in blocked_categories:
                        if pos in obj.category:
                            test = False
                            break

                if test:
                    obj.save()
