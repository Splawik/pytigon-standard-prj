import os

from django.conf import settings
from django.core.management.base import BaseCommand

from schbuilder.models import SChProject
from schbuilder.views import prj_export

PRJS_TO_EXPORT = [
    "schdevtools",  # prepare with initial data
    "schmanage",
    "schscripts",
    "_schsetup",
    "_schot",
    "schportal",
    "schpytigondemo",
    "schwebtrapper",
    "scheditor",  # prepare db but without initial data
    "_schcomponents",
    "scheditor",
    "_schdata",
    "_schremote",
    "_schtools",
    "_schwiki",
    "_schserverless",  # without db
    "schemail",
    "_schall",
    "schodf",
    "_schplaywright",
    "mobile_demo",
    "_schbi",
    "_schbusiness",
]


class Command(BaseCommand):
    help = "Prepare installer files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--prjs",
            default=None,
            help="Specifies projects",
        )
        parser.add_argument(
            "--output-path",
            default=None,
            help="Output path",
        )

    def handle(self, *args, **options):
        if options["prjs"]:
            prjs_to_export = options["prjs"].replace(",", ";").split(";")
        else:
            prjs_to_export = PRJS_TO_EXPORT

        for prj_name in prjs_to_export:
            if not prj_name:
                continue
            prjs = list(SChProject.objects.filter(name=prj_name, main_view=True))
            if len(prjs) > 0:
                prj = prjs[-1]
                x = prj_export(None, prj.pk)

                if "output_path" in options:
                    output_path = options["output_path"]
                else:
                    output_path = os.path.join(settings.DATA_PATH, "install")
                print("Output path: ", output_path)
                print(options)

                path = os.path.join(output_path, f"{prj_name}.ptigprj")
                print("Export prj: ", path)
                with open(path, "wt") as f:
                    if type(x.content) == bytes:
                        f.write(x.content.decode("utf-8"))
                    else:
                        f.write(x.content)
