from rest_framework import serializers
from django.db.models import Avg
from .models import Product, Category, Color, Brand, Review, Banner
from .utils import round_to_nearest_half
from cloudinary.forms import CloudinaryFileField
from django.conf import settings
class CategorySerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['label', 'value']

    def get_value(self, obj):
        translation = {
            'Холодильник': 'refrigerator',
            'Стиральная машина': 'washing machine',
            'Посудомоечная машина': 'dishwasher',
            'Микроволновая печь': 'microwave',
            'Телевизор': 'television',
            'Пылесос': 'vacuum cleaner',
            'Кондиционер': 'air conditioner',
            'Печь': 'oven',
            'Фен': 'hair dryer',
            'Тостер': 'toaster',
            'Кофеварка': 'coffee maker',
            'Электрический чайник': 'electric kettle',
            'Утюг': 'iron',
            'Блендер': 'blender',
            'Соковыжималка': 'juicer',
            'Сушилка для белья': 'clothes dryer',
            'Кухонный комбайн': 'food processor',
            'Вентилятор': 'fan',
            'Холодильная камера': 'cold storage',
            'Водонагреватель': 'water heater',
            'Мясорубка': 'meat grinder',
            'Вафельница': 'waffle maker',
            'Суповарка': 'soup maker',
            'Электрическая духовка': 'electric oven',
            'Мясопереработчик': 'meat slicer',
            'Бассейн': 'pool',
            'Система фильтрации воды': 'water filtration system',
            'Кухонные весы': 'kitchen scale',
            'Размораживатель': 'defroster',
            'Хлебопечка': 'bread maker',
        }

        if obj.value:
            return translation.get(obj.value, obj.value)
        return translation.get(obj.label.lower(), obj.label.lower())

    def get_label(self, obj):
        # Возвращаем label с первой заглавной буквой
        return obj.label.capitalize()

    def create(self, validated_data):
        label = validated_data.get('label')

        translation = {
            'Холодильник': 'refrigerator',
            'Стиральная машина': 'washing machine',
            'Посудомоечная машина': 'dishwasher',
            'Микроволновая печь': 'microwave',
            'Телевизор': 'television',
            'Пылесос': 'vacuum cleaner',
            'Кондиционер': 'air conditioner',
            'Печь': 'oven',
            'Фен': 'hair dryer',
            'Тостер': 'toaster',
            'Кофеварка': 'coffee maker',
            'Электрический чайник': 'electric kettle',
            'Утюг': 'iron',
            'Блендер': 'blender',
            'Соковыжималка': 'juicer',
            'Сушилка для белья': 'clothes dryer',
            'Кухонный комбайн': 'food processor',
            'Вентилятор': 'fan',
            'Холодильная камера': 'cold storage',
            'Водонагреватель': 'water heater',
            'Мясорубка': 'meat grinder',
            'Вафельница': 'waffle maker',
            'Суповарка': 'soup maker',
            'Электрическая духовка': 'electric oven',
            'Мясопереработчик': 'meat slicer',
            'Бассейн': 'pool',
            'Система фильтрации воды': 'water filtration system',
            'Кухонные весы': 'kitchen scale',
            'Размораживатель': 'defroster',
            'Хлебопечка': 'bread maker',
        }

        validated_data['value'] = translation.get(label.lower(), label.lower())
        return super().create(validated_data)

class ColorSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()

    class Meta:
        model = Color
        fields = ['label', 'value']

    def get_value(self, obj):
        # Словарь для перевода значений на английский
        translation = {
            'белый': 'white',
            'черный': 'black',
            'красный': 'red',
            'синий': 'blue',
            'зеленый': 'green',
            'желтый': 'yellow',
            'оранжевый': 'orange',
            'пурпурный': 'purple',
            'розовый': 'pink',
            'серый': 'gray',
            'коричневый': 'brown',
            'бежевая': 'beige',
            'фиолетовый': 'violet',
            'голубой': 'light blue',
            'бирюзовый': 'turquoise',
            'мятный': 'mint',
            'лавандовый': 'lavender',
            'гранатовый': 'pomegranate',
            'песочный': 'sand',
            'оливковый': 'olive',
            'малахитовый': 'malachite',
            'медный': 'copper',
            'слоновая кость': 'ivory',
        }

        # Проверяем, есть ли значение
        if obj.value:
            # Возвращаем значение на английском, если оно есть в словаре
            return translation.get(obj.value, obj.value)

        # Если значения нет, возвращаем значение на английском по label
        return translation.get(obj.label.lower(), obj.label.lower())

    def create(self, validated_data):
        label = validated_data.get('label').lower()

        # Словарь для перевода значений на английский
        translation = {
            'белый': 'white',
            'черный': 'black',
            'красный': 'red',
            'синий': 'blue',
            'зеленый': 'green',
            'желтый': 'yellow',
            'оранжевый': 'orange',
            'пурпурный': 'purple',
            'розовый': 'pink',
            'серый': 'gray',
            'коричневый': 'brown',
            'бежевая': 'beige',
            'фиолетовый': 'violet',
            'голубой': 'light blue',
            'бирюзовый': 'turquoise',
            'мятный': 'mint',
            'лавандовый': 'lavender',
            'гранатовый': 'pomegranate',
            'песочный': 'sand',
            'оливковый': 'olive',
            'малахитовый': 'malachite',
            'медный': 'copper',
            'слоновая кость': 'ivory',
        }

        # Присваиваем value на основе label
        validated_data['value'] = translation.get(label, label)

        return super().create(validated_data)

class BrandSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ['label', 'value']

    def get_value(self, obj):
        translation = {
            'Acer': 'ACER',
            'Amazon': 'AMAZON',
            'Apple': 'APPLE',
            'Asus': 'ASUS',
            'Barnes & Noble': 'BARNES & NOBLE',
            'Blackberry': 'BLACKBERRY',
            'Bosch': 'BOSCH',
            'Bose': 'BOSE',
            'Canon': 'CANON',
            'Dell': 'DELL',
            'Denon': 'DENON',
            'Garmin': 'GARMIN',
            'Hewlett Packard': 'HEWLETT PACKARD',
            'Htc': 'HTC',
            'Lenovo': 'LENOVO',
            'LG': 'LG',
            'Microsoft': 'MICROSOFT',
            'Motorola': 'MOTOROLA',
            'Newegg': 'NEWEGG',
            'Nexus': 'NEXUS',
            'Nikon': 'NIKON',
            'Nokia': 'NOKIA',
            'Olloclip': 'OLLOCLIP',
            'Olympus': 'OLYMPUS',
            'Panasonic': 'PANASONIC',
            'Philips': 'PHILIPS',
            'Pioneer': 'PIONEER',
            'Radioshack': 'RADIOSHACK',
            'Ricoh': 'RICOH',
            'Samsung': 'SAMSUNG',
            'Sharp': 'SHARP',
            'Sony': 'SONY',
            'Tomtom': 'TOMTOM',
            'Toshiba': 'TOSHIBA',
            'Xbox': 'XBOX',
        }

        # Если значение value уже есть
        if obj.value:
            return translation.get(obj.value, obj.value).upper()

        # Если value нет, присваиваем его на основе label
        return translation.get(obj.label, obj.label).upper()

    def create(self, validated_data):
        label = validated_data.get('label')

        translation = {
            'Acer': 'ACER',
            'Amazon': 'AMAZON',
            'Apple': 'APPLE',
            'Asus': 'ASUS',
            'Barnes & Noble': 'BARNES & NOBLE',
            'Blackberry': 'BLACKBERRY',
            'Bosch': 'BOSCH',
            'Bose': 'BOSE',
            'Canon': 'CANON',
            'Dell': 'DELL',
            'Denon': 'DENON',
            'Garmin': 'GARMIN',
            'Hewlett Packard': 'HEWLETT PACKARD',
            'Htc': 'HTC',
            'Lenovo': 'LENOVO',
            'LG': 'LG',
            'Microsoft': 'MICROSOFT',
            'Motorola': 'MOTOROLA',
            'Newegg': 'NEWEGG',
            'Nexus': 'NEXUS',
            'Nikon': 'NIKON',
            'Nokia': 'NOKIA',
            'Olloclip': 'OLLOCLIP',
            'Olympus': 'OLYMPUS',
            'Panasonic': 'PANASONIC',
            'Philips': 'PHILIPS',
            'Pioneer': 'PIONEER',
            'Radioshack': 'RADIOSHACK',
            'Ricoh': 'RICOH',
            'Samsung': 'SAMSUNG',
            'Sharp': 'SHARP',
            'Sony': 'SONY',
            'Tomtom': 'TOMTOM',
            'Toshiba': 'TOSHIBA',
            'Xbox': 'XBOX',
        }

        # Присваиваем value на основе label
        validated_data['value'] = translation.get(label, label).upper()

        return super().create(validated_data)

class ReviewSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'comments','created']

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    main_characteristics = serializers.JSONField()
    reviews = ReviewSummarySerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'category',
            'color',
            'images',
            'price',
            'promotion',
            'brand',
            'quantity',
            'description',
            'is_product_of_the_day',
            'avg_rating',
            'reviews',
            'is_active',
            'main_characteristics',
        ]

    def get_avg_rating(self, obj):
        if obj.reviews.exists():
            avg_rating = obj.reviews.aggregate(Avg('rating'))['rating__avg']
            return round(avg_rating, 1) if avg_rating else 0
        return 0

    def get_images(self, obj):
        request = self.context.get('request')
        images = [
            obj.image1.url if obj.image1 else None,
            obj.image2.url if obj.image2 else None,
            obj.image3.url if obj.image3 else None,
            obj.image4.url if obj.image4 else None,
            obj.image5.url if obj.image5 else None,
        ]
        return [request.build_absolute_uri(image) for image in images if image] if request else images

    def validate_main_characteristics(self, value):
        # Если значение None, преобразуем его в пустой список
        if value is None:
            value = []

        if not isinstance(value, list):
            raise serializers.ValidationError("Характеристики должны быть списком.")

        if len(value) > 4:
            raise serializers.ValidationError("Нельзя добавлять более 4 характеристик.")

        for characteristic in value:
            if not isinstance(characteristic, dict):
                raise serializers.ValidationError("Каждая характеристика должна быть объектом (ключ: значение).")
            if 'key' not in characteristic or 'value' not in characteristic:
                raise serializers.ValidationError("Каждая характеристика должна содержать ключ и значение.")
            if not isinstance(characteristic['key'], str):
                raise serializers.ValidationError("Ключ характеристики должен быть строкой.")
            if not isinstance(characteristic['value'], str) and not isinstance(characteristic['value'], (int, float)):
                raise serializers.ValidationError(
                    "Значение характеристики должно быть строкой, числом или числом с плавающей точкой.")

        return value


class ProductShortSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'images',
            'avg_rating',
            'title',
            'price',
            'promotion',
        ]

    def get_avg_rating(self, obj):
        if obj.reviews.exists():
            avg_rating = obj.reviews.aggregate(Avg('rating'))['rating__avg']
            return round_to_nearest_half(avg_rating)
        return 0

    def get_images(self, obj):
        request = self.context.get('request')
        images = [
            obj.image1.url if obj.image1 else None,

        ]
        if request:
            return [request.build_absolute_uri(image) for image in images if image]
        return [image for image in images if image]

class ProductCreateSerializer(serializers.ModelSerializer):
    main_characteristics = serializers.JSONField()
    characteristics = serializers.JSONField(required=False)  # Если у вас есть поле для характеристик

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'category',
            'color',
            'image1',
            'image2',
            'image3',
            'image4',
            'image5',
            'price',
            'promotion',
            'wholesale_price',
            'wholesale_promotion',
            'brand',
            'quantity',
            'description',
            'is_product_of_the_day',
            'is_active',
            'main_characteristics',
            'characteristics',  # Добавлено поле для характеристик
        ]

    def to_representation(self, instance):
        """Переопределение вывода данных для пользователей, учитывая их роль."""
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            user = request.user
            if user.role == 'wholesaler':  # Если роль оптовика
                representation['price'] = instance.wholesale_price
                representation['promotion'] = instance.wholesale_promotion
            else:  # Если обычный клиент
                representation['price'] = instance.price
                representation['promotion'] = instance.promotion

        return representation

    def create(self, validated_data):
        """Создание продукта с характеристиками."""
        characteristics_data = validated_data.pop('characteristics', [])
        product = Product.objects.create(**validated_data)

        # Получаем текущего пользователя из контекста
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            if user.role == 'wholesaler':  # Если роль оптовика
                product.price = product.wholesale_price
                product.promotion = product.wholesale_promotion

        # Сохранение объекта продукта
        product.save()

        # Создание характеристик продукта
        for char_data in characteristics_data:
            ProductCharacteristic.objects.create(product=product, **char_data)

        return product

    def update(self, instance, validated_data):
        """Обновление продукта и его характеристик."""
        characteristics_data = validated_data.pop('characteristics', [])
        instance = super().update(instance, validated_data)

        # Получаем текущего пользователя из контекста
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            if user.role == 'wholesaler':  # Если роль оптовика
                instance.price = instance.wholesale_price
                instance.promotion = instance.wholesale_promotion

        # Сохраняем обновленный продукт
        instance.save()

        # Удаляем старые характеристики
        instance.characteristics.all().delete()

        # Создаем новые характеристики
        for char_data in characteristics_data:
            ProductCharacteristic.objects.create(product=instance, **char_data)

        return instance


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['product','rating','comments','created','updated']



    def create(self, validated_data):
        # Добавляем текущего пользователя из запроса
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BannerSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ('id', 'image')

    def get_image(self, obj):
        # Если изображение существует, генерируем полный URL
        if obj.image:
            return f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/{obj.image}"
        return None