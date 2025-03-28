# Generated by Django 5.1.3 on 2025-01-09 14:12

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0054_alter_product_image1_alter_product_image2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image4',
            field=cloudinary.models.CloudinaryField(default=1, max_length=255, verbose_name='image4'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='image5',
            field=cloudinary.models.CloudinaryField(default=1, max_length=255, verbose_name='image5'),
            preserve_default=False,
        ),
    ]
