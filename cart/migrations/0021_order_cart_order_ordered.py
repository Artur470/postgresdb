# Generated by Django 5.1.2 on 2025-02-23 04:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0020_remove_order_cart_remove_order_ordered_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cart',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cart.cart'),
        ),
        migrations.AddField(
            model_name='order',
            name='ordered',
            field=models.BooleanField(default=False),
        ),
    ]
