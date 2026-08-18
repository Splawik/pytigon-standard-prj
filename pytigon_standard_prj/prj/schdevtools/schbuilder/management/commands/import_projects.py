import os

from django.conf import settings
from django.core.management.base import BaseCommand
from schbuilder.models import SChProject
from schbuilder.views import prj_import_from_str

import pytigon_standard_prj

PRJS_TO_IMPORT = [
    "schdevtools",  # prepare with initial data
    "schmanage",
    "schscripts",
    "_schsetup",
    "schportal",
    "schpytigondemo",
    "schwebtrapper",
    "scheditor",  # prepare db but without initial data
    "_schcomponents",
    "_schdata",
    "_schremote",
    "_schtools",
    "_schwiki",
    "_schserverless",  # without db
]


class Command(BaseCommand):
    help = "Prepare installer files"

    def add_arguments(self, parser):
        parser.add_argument(
            "prj_name", nargs="?", help="Project name, all - for all projects"
        )

    def handle(self, *args, **options):
        if options.get("prj_name"):
            if options["prj_name"] == "all":
                projects = PRJS_TO_IMPORT
            else:
                projects = [options["prj_name"]]
        else:
            projects = PRJS_TO_IMPORT

        for prj_name in projects:
            prjs = list(SChProject.objects.filter(name=prj_name))
            if len(prjs) == 0:
                path = os.path.join(
                    os.path.join(settings.DATA_PATH, "install"), f"{prj_name}.ptigprj"
                )
                if not os.path.exists(path):
                    path = os.path.join(
                        os.path.join(pytigon_standard_prj.__path__[0], "install"),
                        f"{prj_name}.ptigprj",
                    )
                print("Import prj: ", path)
                try:
                    with open(path, "rt") as f:
                        s = f.read()
                        prj_import_from_str(s)
                except:
                    print("Prj: ", path, " not imported!")
