from django.db import models
from django.contrib.auth import get_user_model
from product.models import Product
from share.models import BaseModel

User = get_user_model()


class Wishlist(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')

    class Meta:
        unique_together = ('created_by', 'product')

    def __str__(self):
        return f"{self.created_by} added {self.product} to wishlist"
