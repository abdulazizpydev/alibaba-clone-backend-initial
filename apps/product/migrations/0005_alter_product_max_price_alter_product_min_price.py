# Generated by Django 4.2.14 on 2024-09-11 03:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0004_remove_product_price_product_max_price_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="max_price",
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name="product",
            name="min_price",
            field=models.FloatField(blank=True, default=0),
        ),
    ]