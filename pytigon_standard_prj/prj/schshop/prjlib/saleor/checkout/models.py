"""Checkout-related ORM models."""
from decimal import Decimal
from operator import attrgetter
from uuid import uuid4

from django.conf import settings
#from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.encoding import smart_str
from django_prices.models import MoneyField
from prices import Money

from ..account.models import Address
from ..core.models import ModelWithMetadata
from ..core.taxes import zero_money
from ..core.weight import zero_weight
from ..giftcard.models import GiftCard
from ..shipping.models import ShippingMethod

# SCH++
from big_company.models import get_profile_id
import sys, traceback
# SCH--

CENTS = Decimal("0.01")


class CheckoutQueryset(models.QuerySet):
    """A specialized queryset for dealing with checkouts."""

    def for_display(self):
        """Annotate the queryset for display purposes.

        Prefetches additional data from the database to avoid the n+1 queries
        problem.
        """

    # SCH++
        #print("for_display")
        return self.prefetch_related(
            "lines__variant__translations",
            "lines__variant__product__translations",
            "lines__variant__product__images",
            "lines__variant__product__product_type__product_attributes__values",
        )  # noqa
        #ret = self.prefetch_related(
        ##    "lines__variant__translations",
        #    "lines__variant__product__translations",
        #    "lines__variant__product__images",
        #    "lines__variant__product__product_type__product_attributes__values",
        #)  # noqa
        #return mod_chckout_queryset(ret)
        #return CheckoutProxy(ret)


    # SCH--



class Checkout(ModelWithMetadata):
    """A shopping checkout."""

# SCH++


    #def __init__(self, *argi, **argv):
        #super().__init__(*argi, **argv)
        #print("Checkout:", argv)
        #print("U2", self.token)
        #if not 'token' in argv:
        #    self.token = uuid4()
        #print("U3", self.token)

    profile_str = models.CharField(max_length=255, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        pid = get_profile_id()
        if pid:            
            self.profile_str = pid
            return super().save(*args, **kwargs)

        return super().save(*args, **kwargs)
        
        
# SCH--

    created = models.DateTimeField(auto_now_add=True)
    last_change = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="checkouts",
        on_delete=models.CASCADE,
    )
    email = models.EmailField()
    token = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    quantity = models.PositiveIntegerField(default=0)
    billing_address = models.ForeignKey(
        Address, related_name="+", editable=False, null=True, on_delete=models.SET_NULL
    )
    shipping_address = models.ForeignKey(
        Address, related_name="+", editable=False, null=True, on_delete=models.SET_NULL
    )
    shipping_method = models.ForeignKey(
        ShippingMethod,
        blank=True,
        null=True,
        related_name="checkouts",
        on_delete=models.SET_NULL,
    )
    note = models.TextField(blank=True, default="")

    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY,
    )

    discount_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    discount = MoneyField(amount_field="discount_amount", currency_field="currency")
    discount_name = models.CharField(max_length=255, blank=True, null=True)

    translated_discount_name = models.CharField(max_length=255, blank=True, null=True)
    voucher_code = models.CharField(max_length=12, blank=True, null=True)
    gift_cards = models.ManyToManyField(GiftCard, blank=True, related_name="checkouts")

# SCH++
    objects = CheckoutQueryset.as_manager()
    #objects = CheckoutProxy(CheckoutQueryset.as_manager())
    #@classmethod
    #def get_objects(cls):
    #    pid = get_profile_id()
    #    if pid:
    #        return cls._objects.filter(profile_str = pid) 
    #    else:
    #        return cls._objects

    #objects = property(get_objects)

    #objects = CheckoutQueryset_as_manager(CheckoutQueryset)

    def weight(self):
        w = 0
        x = self.lines.all()
        for pos in x:
            if pos.variant.weight2:
                w += pos.variant.weight.standard * pos.quantity
        return w
        
    def weight_is_ok(self):
        if self.weight() < 24000:
            return True
        else:
            return False
        return False
    
# SCH--

    class Meta:
        ordering = ("-last_change",)

    def __repr__(self):
        return "Checkout(quantity=%s)" % (self.quantity,)

    def __iter__(self):
        return iter(self.lines.all())

    def __len__(self):
        return self.lines.count()

    def get_customer_email(self):
        return self.user.email if self.user else self.email

    def is_shipping_required(self):
        """Return `True` if any of the lines requires shipping."""
        return any(line.is_shipping_required() for line in self)

    def get_shipping_price(self):
        return (
            self.shipping_method.get_total()
            if self.shipping_method and self.is_shipping_required()
            else zero_money(self.currency)
        )

    def get_subtotal(self, discounts=None):
        """Return the total cost of the checkout prior to shipping."""
        subtotals = (line.get_total(discounts) for line in self)
        #print(self.currency)
        #self.currency='PLN'
        return sum(subtotals, zero_money(currency=self.currency))

    def get_total(self, discounts=None):
        """Return the total cost of the checkout."""
        total = self.get_subtotal(discounts) + self.get_shipping_price() - self.discount
        return max(total, zero_money(total.currency))

    def get_total_gift_cards_balance(self):
        """Return the total balance of the gift cards assigned to the checkout."""
        balance = self.gift_cards.aggregate(models.Sum("current_balance_amount"))[
            "current_balance_amount__sum"
        ]
        if balance is None:
            return zero_money(currency=self.currency)
        return Money(balance, self.currency)

    def get_total_weight(self):
        # Cannot use `sum` as it parses an empty Weight to an int
        weights = zero_weight()
        for line in self:
            weights += line.variant.get_weight() * line.quantity
        return weights

    def get_line(self, variant):
        """Return a line matching the given variant and data if any."""
        matching_lines = (line for line in self if line.variant.pk == variant.pk)
        return next(matching_lines, None)

    def get_last_active_payment(self):
        payments = [payment for payment in self.payments.all() if payment.is_active]
        return max(payments, default=None, key=attrgetter("pk"))


class CheckoutLine(models.Model):
    """A single checkout line.

    Multiple lines in the same checkout can refer to the same product variant if
    their `data` field is different.
    """

    checkout = models.ForeignKey(
        Checkout, related_name="lines", on_delete=models.CASCADE
    )
    variant = models.ForeignKey(
        "product.ProductVariant", related_name="+", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        unique_together = ("checkout", "variant", "data")
        ordering = ("id",)

    def __str__(self):
        return smart_str(self.variant)

    __hash__ = models.Model.__hash__

    def __eq__(self, other):
        if not isinstance(other, CheckoutLine):
            return NotImplemented

        return self.variant == other.variant and self.quantity == other.quantity

    def __ne__(self, other):
        return not self == other  # pragma: no cover

    def __repr__(self):
        return "CheckoutLine(variant=%r, quantity=%r)" % (self.variant, self.quantity)

    def __getstate__(self):
        return self.variant, self.quantity

    def __setstate__(self, data):
        self.variant, self.quantity = data

    def get_total(self, discounts=None):
        """Return the total price of this line."""
        amount = self.quantity * self.variant.get_price(discounts)
        return amount.quantize(CENTS)

    def is_shipping_required(self):
        """Return `True` if the related product variant requires shipping."""
        return self.variant.is_shipping_required()
