# Generated by Django 5.1.2 on 2025-02-20 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0015_remove_order_total_price_remove_order_total_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='role',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
