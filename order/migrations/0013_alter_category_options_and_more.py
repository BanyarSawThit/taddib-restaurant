# Generated by Django 5.1.7 on 2025-03-20 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_rename_is_available_table_availability_table_qr_code'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.RenameField(
            model_name='category',
            old_name='category_title',
            new_name='title',
        ),
        migrations.RemoveField(
            model_name='category',
            name='cate_image',
        ),
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='table',
            name='table_number',
            field=models.PositiveIntegerField(unique=True),
        ),
    ]
