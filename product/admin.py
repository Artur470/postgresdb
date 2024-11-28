from django.contrib import admin
from .models import Category, Product, Banner, Color

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'quantity', 'is_active']
    fields = ('title', 'image1', 'image2', 'image3', 'image4','image5','category', 'color', 'price', 'promotion', 'brand', 'quantity', 'description', 'is_product_of_the_day', 'is_active', )

admin.site.register(Category)
admin.site.register(Banner)
admin.site.register(Color)

