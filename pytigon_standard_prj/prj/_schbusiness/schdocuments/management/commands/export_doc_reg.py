from django.core.management.base import BaseCommand, CommandError

import sys
import io
import os
import getopt

from django.conf import settings
from pytigon_lib.schtools import schjson
from schelements.models import DocReg, DocType, DocRegStatus

REG_ATTRS = (
    'name', 'app', 'group', 'description', 'head_form', 'head_template', 'item_form', 'item_template', 'save_head_fun', 'save_item_fun', 'access_fun', 'update_time', 
)

REGTYPE_ATTRS = (
    'name', 'description', 'correction', 'head_form', 'head_template', 'item_form', 'item_template', 'save_head_fun', 'save_item_fun', 'doctype_status', 'update_time', 
)


STATUS_ATTRS = (
    'order', 'name', 'description', 'icon', 'accept_proc', 'undo_proc', 'can_set_proc', 'can_undo_proc', 'accept_form', 'undo_form', 'for_accept_template', 'for_undo_template', 
)


class Command(BaseCommand):
    help ="Export document register"

    def add_arguments(self, parser):
        parser.add_argument(
            'reg_name', 
            nargs="?",
            help='register name',
        )
        
    def handle(self, *args, **options):
        ret = {}
        if options['reg_name']:
            reg_name = options['reg_name']
            obj = DocReg.objects.filter(name=reg_name).first()
            if obj:
                for attr in REG_ATTRS:
                    ret[attr] = getattr(obj, attr)
                ret['statuses'] = []
                ret['types'] = []
                statuses = obj.docregstatus_set.all()
                for status in statuses:
                    s = {}
                    for attr in STATUS_ATTRS:
                        s[attr] = getattr(status, attr)
                    ret['statuses'].append(s)
                types = obj.doctype_set.all()
                for t in types:
                    x = {}
                    for attr in REGTYPE_ATTRS:
                        x[attr] = getattr(t, attr)
                    ret['types'].append(x)
            
            print(schjson.json_dumps(ret))
