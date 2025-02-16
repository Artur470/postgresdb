# Generated by Django 5.1.2 on 2024-11-26 07:16

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0036_remove_review_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comments', models.TextField(blank=True, null=True, verbose_name='Comments')),
                ('rating', models.FloatField(choices=[(1, '1 star'), (1.5, '1.5 star'), (2, '2 star'), (2.5, '2.5 star'), (3, '3 star'), (3.5, '3.5 star'), (4, '4 star'), (4.5, '4.5 star'), (5, '5 star')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Rating')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Date Updated')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='product.product', verbose_name='Product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.DeleteModel(
            name='Review',
        ),
    ]
