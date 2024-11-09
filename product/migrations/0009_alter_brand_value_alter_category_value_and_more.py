# Generated by Django 5.1.1 on 2024-10-03 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_alter_product_brand_alter_product_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='value',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='value',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='color',
            name='value',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]