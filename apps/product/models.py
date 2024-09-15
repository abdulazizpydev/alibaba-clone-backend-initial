import uuid

from django.db import models
from django.contrib.auth import get_user_model
from share.models import BaseModel
from mptt.models import MPTTModel, TreeForeignKey

User = get_user_model()


def category_image_path(instance, filename):
    return "category/icons/{}/{}".format(instance.name, filename)


def product_image_path(instance, filename):
    return "products/{}/images/{}".format(instance.product.id, filename)


class Category(MPTTModel):
    id = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, primary_key=True
    )
    name = models.CharField(max_length=200)
    parent = TreeForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)
    hex_value = models.CharField(max_length=7)

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(BaseModel):
    seller = models.ForeignKey(
        User, related_name="user_product", on_delete=models.CASCADE
    )
    category = TreeForeignKey(
        Category, related_name="product_category", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=250)
    price = models.FloatField(default=0, blank=True)
    description = models.TextField(null=True, blank=True)
    colors = models.ManyToManyField(Color, related_name="products", blank=True)
    sizes = models.ManyToManyField(Size, related_name="products", blank=True)
    quantity = models.IntegerField(default=1)
    views = models.IntegerField(default=0)

    def __str__(self):
        return str(f"{self.title} - {self.category}")


class Image(BaseModel):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=product_image_path, blank=True)

    def __str__(self):
        return f"Image for {self.product.title} - {self.id}"


class ProductViews(BaseModel):
    ip = models.CharField(max_length=250)
    product = models.ForeignKey(
        Product, related_name="product_views", on_delete=models.CASCADE
    )
