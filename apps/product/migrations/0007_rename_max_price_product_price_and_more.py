# Generated by Django 4.2.14 on 2024-09-13 04:23

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0006_remove_category_icon"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="max_price",
            new_name="price",
        ),
        migrations.RemoveField(
            model_name="product",
            name="min_price",
        ),
    ]