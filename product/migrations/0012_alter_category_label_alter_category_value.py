# Generated by Django 5.1.1 on 2024-10-04 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_alter_category_label_alter_category_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='label',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='category',
            name='value',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
