# Generated by Django 4.2.7 on 2025-04-21 13:57

from django.db import migrations
import django_bleach.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_product_fresh_description_product_iqf_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=django_bleach.models.BleachField(blank=True, null=True, verbose_name='Description'),
        ),
    ]
