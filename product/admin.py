from django.contrib import admin
from .models import Category, Product, Banner, Color
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import JSONField, ModelForm
from .models import Product

class ProductAdminForm(ModelForm):
    """
    Форма для модели Product с проверкой количества характеристик.
    """
    features = JSONField(required=False, help_text="Добавьте характеристики в формате JSON (не более 4).")

    def clean_features(self):
        features = self.cleaned_data.get('features', [])
        if len(features) > 4:
            raise ValidationError("Нельзя добавлять более 4 характеристик для одного товара.")
        return features

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['title', 'category', 'price', 'quantity', 'is_active']
    fields = (
        'title',
        'image1',
        'image2',
        'image3',
        'image4',
        'image5',
        'category',
        'color',
        'price',
        'promotion',
        'brand',
        'quantity',
        'description',
        'main_characteristics',
        'is_product_of_the_day',
        'is_active',
    )
    search_fields = ['title', 'category__name', 'brand__name']  # Добавлено для поиска
    list_filter = ['category', 'brand', 'is_active']  # Фильтры

    def save_model(self, request, obj, form, change):
        """
        Проверка при сохранении из админки.
        """
        if len(obj.features) > 4:
            raise ValidationError("Нельзя добавлять более 4 характеристик для одного товара.")
        super().save_model(request, obj, form, change)
admin.site.register(Category)
admin.site.register(Banner)
admin.site.register(Color)

