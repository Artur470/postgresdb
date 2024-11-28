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
        fields = ['id', 'rating', 'comments']



class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    reviews = ReviewSummarySerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()


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
            'reviews',
            'avg_rating',
            'is_active',

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
            obj.image2.url if obj.image2 else None,
            obj.image3.url if obj.image3 else None,
            obj.image4.url if obj.image4 else None,
            obj.image5.url if obj.image5 else None,
        ]
        return [request.build_absolute_uri(image) for image in images if image] if request else images


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

# class ProductCharacteristicSerializer(serializers.ModelSerializer):
#      class Meta:
#             model = ProductCharacteristic
#             fields = ['key', 'value']
#

class ProductCreateSerializer(serializers.ModelSerializer):
    # characteristics = ProductCharacteristicSerializer(many=True, required=False)

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
            'brand',
            'quantity',
            'description',
            'is_product_of_the_day',
            # 'characteristics',

        ]

    def to_representation(self, instance):
        """Переопределение вывода данных."""
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            images = [
                request.build_absolute_uri(instance.image1.url) if instance.image1 else None,
                request.build_absolute_uri(instance.image2.url) if instance.image2 else None,
                request.build_absolute_uri(instance.image3.url) if instance.image3 else None,
                request.build_absolute_uri(instance.image4.url) if instance.image4 else None,
                request.build_absolute_uri(instance.image5.url) if instance.image5 else None,
            ]
            representation['images'] = [image for image in images if image]
            # Удаляем поля image1, image2, image3 из вывода
            representation.pop('image1', None)
            representation.pop('image2', None)
            representation.pop('image3', None)
            representation.pop('image4', None)
            representation.pop('image5', None)
        return representation

    def create(self, validated_data):
        """Создание продукта с характеристиками."""
        characteristics_data = validated_data.pop('characteristics', [])
        product = Product.objects.create(**validated_data)
        for char_data in characteristics_data:
            ProductCharacteristic.objects.create(product=product, **char_data)
        return product

    def update(self, instance, validated_data):
        """Обновление продукта и его характеристик."""
        characteristics_data = validated_data.pop('characteristics', [])
        instance = super().update(instance, validated_data)

        # Удаляем старые характеристики
        instance.characteristics.all().delete()

        # Создаём новые характеристики
        for char_data in characteristics_data:
            ProductCharacteristic.objects.create(product=instance, **char_data)

        return instance


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['product', 'comments', 'rating', 'created', 'updated']

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