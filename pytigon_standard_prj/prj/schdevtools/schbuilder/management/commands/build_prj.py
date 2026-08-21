import sys

from django.core.management.base import BaseCommand

from schbuilder.models import SChProject
from schbuilder.views import build_prj


class Command(BaseCommand):
    help = "Build project"

    def add_arguments(self, parser):
        parser.add_argument(
            "prj_name", nargs="?", help="Project name, all - for all projects"
        )
        parser.add_argument(
            "--output",
            help="save output to file",
        )
        parser.add_argument(
            "--forexternaledit",
            help="Generate .py files for external editing",
        )

    def handle(self, *args, **options):
        if not options["prj_name"]:
            self.print_help("manage.py", "build_prj")
            sys.exit(1)

        if options.get("output"):
            o = options["output"]
        else:
            o = None

        if options.get("forexternaledit"):
            c = {}
        else:
            c = {"milestone": True}

        if options["prj_name"] == "all":
            object_list = SChProject.objects.filter(main_view=True)
        else:
            object_list = SChProject.objects.filter(
                main_view=True, name=options["prj_name"]
            )

        for obj in object_list:
            print("\nBUILD: ", obj.name)
            ret = build_prj(obj.pk, c)
            if o:
                with open(o, "wt") as f:
                    f.writelines("%s %s\n"(item[1], item[2]) for item in ret)
            else:
                for item in ret:
                    print("    ", item[1], item[2])
