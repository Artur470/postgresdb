from django.db import models
from config import settings
from cloudinary.models import CloudinaryField
from decimal import Decimal, InvalidOperation


class Category(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Brand(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Color(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/', blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    promotion = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # promotion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Процент скидки
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    quantity = models.IntegerField()
    description = models.TextField(max_length=2551)

    def __str__(self):
        return self.title
