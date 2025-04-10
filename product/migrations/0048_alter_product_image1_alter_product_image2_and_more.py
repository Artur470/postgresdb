# Generated by Django 5.1.3 on 2024-11-30 19:37

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0047_alter_product_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image1',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image1'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image2',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image2'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image3',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image3'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image4',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image4'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image5',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image5'),
        ),
    ]
