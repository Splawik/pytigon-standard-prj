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
    help ="Import document register"

    def add_arguments(self, parser):
        parser.add_argument(
            'file_name', 
            nargs="?",
            help='Name of the imported file',
        )
        
    def handle(self, *args, **options):
        if options['file_name']:
            txt = None
            with open(options['file_name'], "rt") as f:
                txt = f.read()
            if txt:
                reg_dict = schjson.json_loads(txt)
                obj = DocReg()
                for attr in REG_ATTRS:
                    setattr(obj, attr, reg_dict[attr])
                obj.save()
                for status_dict in reg_dict['statuses']:
                    s_obj = DocRegStatus()
                    s_obj.parent = obj
                    for attr in STATUS_ATTRS:
                        setattr(s_obj, attr, status_dict[attr])
                    s_obj.save()
                for type_dict in reg_dict['types']:
                    t_obj = DocType()
                    t_obj.parent = obj
                    for attr in REGTYPE_ATTRS:
                        setattr(t_obj, attr, type_dict[attr])
                    t_obj.save()
