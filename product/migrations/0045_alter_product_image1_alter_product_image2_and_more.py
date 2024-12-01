# Generated by Django 5.1.3 on 2024-11-30 18:57

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0044_alter_product_image1_alter_product_image2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image1',
            field=cloudinary.models.CloudinaryField(default=1, max_length=255, verbose_name='image1'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='image2',
            field=cloudinary.models.CloudinaryField(default=1, max_length=255, verbose_name='image2'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='image3',
            field=cloudinary.models.CloudinaryField(default=1, max_length=255, verbose_name='image3'),
            preserve_default=False,
        ),
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
