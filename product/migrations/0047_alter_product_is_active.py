# Generated by Django 5.1.3 on 2024-11-30 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0046_alter_product_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]