from django.db import models
from django.conf import settings
from django.utils import timezone
from share.models import BaseModel


class Coupon(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed')])
    discount_value = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    active = models.BooleanField(default=True)
    max_uses = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='used_coupons')

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_until and self.used_count < self.max_uses

    def apply_coupon(self, order_amount):
        if self.discount_type == 'percentage':
            return order_amount * (1 - (self.discount_value / 100))
        elif self.discount_type == 'fixed':
            return max(order_amount - self.discount_value, 0)
        return order_amount

    def apply(self):
        """Increment the used count when applied."""
        if self.used_count < self.max_uses:
            self.used_count += 1
            self.save()
        else:
            raise ValueError("Coupon has reached maximum uses")

    def __str__(self):
        return self.code
