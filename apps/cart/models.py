from django.db import models
from user.models import User
from product.models import Product


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_items = models.PositiveIntegerField(default=0)

    def get_total(self):
        return sum(item.get_total_price() for item in self.items.all())

    def update_total_items(self):
        self.total_items = self.items.aggregate(total=models.Sum('quantity'))['total'] or 0
        self.save()

    def empty_cart(self):
        self.items.all().delete()
        self.update_total_items()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.product.price * self.quantity
