# Generated by Django 5.1.7 on 2025-03-24 05:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cart.category')),
            ],
        ),
        migrations.CreateModel(
            name='Customization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meat', models.CharField(blank=True, choices=[('Beef', 'Beef'), ('Chicken', 'Chicken')], max_length=50, null=True)),
                ('spicy_level', models.CharField(blank=True, choices=[('Mild', 'Mild'), ('Medium', 'Medium'), ('High', 'High')], max_length=50, null=True)),
                ('extra_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customizations', to='cart.item')),
            ],
        ),
    ]
