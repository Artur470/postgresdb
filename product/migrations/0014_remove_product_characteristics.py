# Generated by Django 5.1.1 on 2024-10-06 15:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_product_characteristics_alter_brand_label_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='characteristics',
        ),
    ]
