# Generated by Django 5.1.2 on 2025-02-22 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0016_order_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='totalPrice',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
