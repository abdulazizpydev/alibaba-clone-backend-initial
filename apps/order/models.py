from django.db import models
from django.conf import settings
from product.models import Product
from share.enums import OrderStatus, PaymentProvider
from share.models import BaseModel
from .countries import Countries


class Order(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    payment_method = models.CharField(
        max_length=25,
        choices=PaymentProvider.choices(),
        default=PaymentProvider.CARD.value,
    )
    items = models.ManyToManyField(Product, through='OrderItem')
    status = models.CharField(max_length=10, choices=OrderStatus.choices(), default=OrderStatus.PENDING.value)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    state_province_region = models.CharField(max_length=255)
    postal_zip_code = models.CharField(max_length=20)
    country_region = models.CharField(
        max_length=255, choices=Countries.choices, default=Countries.Uzbekistan)
    telephone_number = models.CharField(max_length=255)
    shipping_name = models.CharField(max_length=255, blank=True, null=True)
    shipping_time = models.CharField(max_length=255, blank=True, null=True)
    shipping_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} - {self.user}"


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.title} - {self.quantity} pcs"
