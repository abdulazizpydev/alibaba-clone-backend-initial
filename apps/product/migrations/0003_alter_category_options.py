# Generated by Django 4.2.14 on 2024-09-10 11:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0002_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="category",
            options={"ordering": ["-created_at"], "verbose_name_plural": "Categories"},
        ),
    ]
