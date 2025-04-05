# Generated by Django 5.1.8 on 2025-04-05 08:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0019_payment"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="bar_status",
            field=models.CharField(
                choices=[
                    ("Waiting", "Waiting"),
                    ("Preparing", "Preparing"),
                    ("Ready", "Ready"),
                ],
                default="Waiting",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="kitchen_status",
            field=models.CharField(
                choices=[
                    ("Waiting", "Waiting"),
                    ("Preparing", "Preparing"),
                    ("Ready", "Ready"),
                ],
                default="Waiting",
                max_length=50,
            ),
        ),
    ]
