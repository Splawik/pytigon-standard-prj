from django.core.management.base import BaseCommand
from saleor.order.models import Order
from saleor.order.actions import cancel_order

class Command(BaseCommand):
    help = "Cancel not payed orders"

    def handle(self, *args, **options):
        objs = Order.objects.filter(payments__isnull=True).exclude(status='canceled').exclude(status='fulfilled')
        for obj in objs:
            desc = obj.get_description()
            cancel_order(obj, None, False)
            self.stdout.write(desc + " - cancelled")
