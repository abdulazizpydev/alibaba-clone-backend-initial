# Generated by Django 4.2.14 on 2024-10-03 04:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(fields=("id",), name="unique_user_id"),
        ),
    ]
