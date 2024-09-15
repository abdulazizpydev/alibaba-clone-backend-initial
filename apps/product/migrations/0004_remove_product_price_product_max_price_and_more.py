# Generated by Django 4.2.14 on 2024-09-11 03:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0003_alter_category_options"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="price",
        ),
        migrations.AddField(
            model_name="product",
            name="max_price",
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name="product",
            name="min_price",
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
    ]