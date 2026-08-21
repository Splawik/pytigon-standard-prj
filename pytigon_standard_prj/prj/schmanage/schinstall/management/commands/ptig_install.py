from django.core.management.base import BaseCommand
from pytigon_lib.schtools.install import Ptig


class Command(BaseCommand):
    help = "Install .ptig file"

    def add_arguments(self, parser):
        parser.add_argument(
            "filename",
            help="Pytigon instalation file (*.ptig)",
        )

    def handle(self, *args, **options):
        filename = options["filename"]
        ptig = Ptig(filename)
        ptig.extract_ptig()
