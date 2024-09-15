# Generated by Django 4.2.14 on 2024-09-03 03:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("product", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="productviews",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"is_active": True},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_%(class)ss",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="productviews",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product_views",
                to="product.product",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="category",
            field=mptt.fields.TreeForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product_category",
                to="product.category",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="colors",
            field=models.ManyToManyField(
                blank=True, related_name="products", to="product.color"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"is_active": True},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_%(class)ss",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="seller",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_product",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="sizes",
            field=models.ManyToManyField(
                blank=True, related_name="products", to="product.size"
            ),
        ),
        migrations.AddField(
            model_name="image",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"is_active": True},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_%(class)ss",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="image",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to="product.product",
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="parent",
            field=mptt.fields.TreeForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="product.category",
            ),
        ),
        migrations.AddIndex(
            model_name="productviews",
            index=models.Index(
                condition=models.Q(("is_active", True)),
                fields=["is_active"],
                name="productviews_is_active_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                condition=models.Q(("is_active", True)),
                fields=["is_active"],
                name="product_is_active_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="image",
            index=models.Index(
                condition=models.Q(("is_active", True)),
                fields=["is_active"],
                name="image_is_active_idx",
            ),
        ),
    ]