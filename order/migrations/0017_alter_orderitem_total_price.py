# Generated by Django 5.1.7 on 2025-03-24 03:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0016_alter_orderitem_total_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='total_price',
            field=models.DecimalField(decimal_places=2, editable=False, max_digits=10),
        ),
    ]
