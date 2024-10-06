# Generated by Django 5.0.6 on 2024-10-06 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_alter_category_label_alter_category_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='characteristics',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='brand',
            name='label',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='label',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='color',
            name='label',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
