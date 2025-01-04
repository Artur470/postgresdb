from rest_framework.response import Response
from rest_framework import status
from .models import Brand, Category, Color
from .serializers import ProductCreateSerializer
import logging
from decimal import Decimal
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Avg
from django.db.models import Q
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from product.models import *
from product.serializers import *
from .filters import ProductFilter
from .models import Review
from .pagination import CustomPagination
from .serializers import ReviewSummarySerializer, ReviewCreateSerializer

logger = logging.getLogger(__name__)

class HomepageView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=['product'],
        operation_description="Этот эндпоинт возвращает данные для главной страницы, "
                              "включая баннер, товар дня, новые товары, "
                              "товары со скидками и популярные товары."
                              "Для выбора товара дня, нужно обновить поле `product_of_the_day = True`, "
                              "и этот товар будет отображаться как товар дня."
    )
    def get(self, request, *args, **kwargs):
        # Получаем данные для главной страницы
        banner = Banner.objects.filter(id=1).first()
        product_of_the_day = Product.objects.filter(is_product_of_the_day=True, is_active=True).first()
        new_products = Product.objects.filter(is_active=True).order_by('-id')[:5]
        promotion_products = Product.objects.filter(promotion__isnull=False, is_active=True)[:5]
        popular_products = Product.objects.filter(is_active=True).annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).filter(
            review_count__gt=0
        ).order_by('-avg_rating')[:10]

        # Подготавливаем контекст для сериализаторов, передаем request для получения роли пользователя
        context = {
            'request': request
        }

        # Формируем ответ
        response_data = {
            "homepage": {
                "banner": self.serialize_banner(banner),
                "product_of_the_day": self.serialize_product(product_of_the_day, context),
                "promotion": self.serialize_products(promotion_products, context),
                "popular": self.serialize_products(popular_products, context),
                "new": self.serialize_products(new_products, context),
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def serialize_banner(self, banner):
        if banner:
            # Сериализация баннера
            serializer = BannerSerializer(banner)
            return serializer.data
        return None

    def serialize_product(self, product, context):
        if product:
            # Сериализация продукта для товар дня
            serializer = ProductShortSerializer(product, context=context)
            return serializer.data
        return None

    def serialize_products(self, products, context):
        # Сериализация списка продуктов
        serializer = ProductShortSerializer(products, many=True, context=context)
        return serializer.data

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @swagger_auto_schema(
        tags=['category'],
        operation_description="Этот эндпоинт позволяет получить список "
                              "всех категорий и создать новую категорию."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['category'],
        operation_description="Этот эндпоинт позволяет создать новую категорию."
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Сохраняем новую категорию
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @swagger_auto_schema(
        tags=['category'],
        operation_description="Этот эндпоинт позволяет получить, "
                              "обновить или удалить категорию по ID."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['category'],
        operation_description="Этот эндпоинт позволяет обновить категорию по ID."
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['category'],
        operation_description="Этот эндпоинт позволяет удалить категорию по ID."
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class BrandListCreateView(generics.ListCreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    @swagger_auto_schema(
        tags=['brand'],
        operation_description="Этот эндпоинт позволяет получить список всех брендов и создать новый бренд."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['brand'],
        operation_description="Этот эндпоинт позволяет создать новый бренд."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    @swagger_auto_schema(
        tags=['brand'],
        operation_description="Этот эндпоинт позволяет получить, обновить или удалить бренд по ID."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['brand'],
        operation_description="Этот эндпоинт позволяет обновить бренд по ID."
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['brand'],
        operation_description="Этот эндпоинт позволяет удалить бренд по ID."
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ColorListCreateView(generics.ListCreateAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

    @swagger_auto_schema(
        tags=['color'],
        operation_description="Этот эндпоинт позволяет получить список всех цветов и создать новый цвет."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['color'],
        operation_description="Этот эндпоинт позволяет создать новый цвет."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ColorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

    @swagger_auto_schema(
        tags=['color'],
        operation_description="Этот эндпоинт позволяет получить, обновить или удалить цвет по ID."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['color'],
        operation_description="Этот эндпоинт позволяет обновить цвет по ID."
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['color'],
        operation_description="Этот эндпоинт позволяет удалить цвет по ID."
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True).order_by('id')
    serializer_class = ProductShortSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description', 'price', 'promotion', 'category__label']
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=['product'],
        operation_description="Этот эндпоинт позволяет получить список всех товаров с возможностью поиска и фильтрации."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Реализация фильтрации товаров.
        """
        queryset = super().get_queryset()

        # Получаем значения фильтров из параметров запроса
        category_value = self.request.query_params.get('category', '').strip()
        brand_value = self.request.query_params.get('brand', '').strip()
        color_value = self.request.query_params.get('color', '').strip()
        search_value = self.request.query_params.get('search', '').strip()

        # Создаем объект фильтрации
        filters = Q()

        # Фильтр по категории
        if category_value:
            if Category.objects.filter(value__iexact=category_value).exists():
                filters &= Q(category__value__iexact=category_value)

        # Фильтр по бренду
        if brand_value:
            if Brand.objects.filter(value__iexact=brand_value).exists():
                filters &= Q(brand__value__iexact=brand_value)

        # Фильтр по цвету
        if color_value:
            if Color.objects.filter(value__iexact=color_value).exists():
                filters &= Q(color__value__iexact=color_value)

        # Фильтр по поисковому запросу
        if search_value:
            filters &= Q(title__icontains=search_value) | Q(description__icontains=search_value) | \
                       Q(price__icontains=search_value) | Q(promotion__icontains=search_value) | \
                       Q(category__label__icontains=search_value)

        # Применяем фильтры к queryset
        queryset = queryset.filter(filters)

        return queryset

    def get_serializer_context(self):
        """
        Передача `request` в контекст сериализатора для корректной работы логики.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=['product'],
        operation_description="Этот эндпоинт позволяет посмотреть похожие товары, "
                              "на товар который мы выбрали через ID, "
                              "схожесть выбирается по категории и по цене товара."
    )
    def get_similar_products(self, product):
        price = Decimal(product.price)
        price_range = Decimal('0.2') * price

        # Фильтрация похожих товаров по категории и цене
        similar_products = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id).filter(
            price__gte=price - price_range,
            price__lte=price + price_range
        ).distinct()

        # Сериализация похожих товаров
        serializer = ProductShortSerializer(similar_products, many=True, context=self.get_serializer_context())
        return serializer.data

    @swagger_auto_schema(
        tags=['product'],
        operation_description="Этот эндпоинт позволяет получить, обновить или удалить продукт по ID."
    )
    def get(self, request, *args, **kwargs):
        product = self.get_object()  # Получаем объект продукта
        # Сериализация данных продукта с учетом роли пользователя
        data = self.get_product_data(product, request)

        # Получаем похожие товары
        data['similar_products'] = self.get_similar_products(product)

        return Response(data)

    @swagger_auto_schema(
        tags=['product'],
        operation_description="Этот эндпоинт позволяет обновить продукт по ID."
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['product'],
        operation_description="Этот эндпоинт позволяет удалить продукт по ID."
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_product_data(self, product, request):
        """
        Получение данных о продукте с учетом цены в зависимости от роли пользователя.
        """
        data = ProductSerializer(product).data

        # Проверяем, если пользователь авторизован и меняем цену в зависимости от его роли
        if request.user.is_authenticated:
            user = request.user
            if user.role == 'wholesaler':  # Для оптовиков показываем оптовые цены
                # Обновляем цену и промо-цену для оптовика
                data['price'] = product.wholesale_price if product.wholesale_price else product.price
                data['promotion'] = product.wholesale_promotion if product.wholesale_promotion else product.promotion
            else:  # Для обычных пользователей — обычные цены
                data['price'] = product.price
                data['promotion'] = product.promotion

        return data


class ProductNewView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductShortSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'price', 'promotion', 'description']

    @swagger_auto_schema(
        tags=['product'],
        operation_description="Этот эндпоинт позволяет получить список новинок товаров."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Product.objects.all().order_by('-id')


class ProductPromotionView(generics.ListAPIView):
    queryset = Product.objects.filter(promotion__isnull=False, is_active=True)
    serializer_class = ProductShortSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'price', 'promotion', 'description']

    @swagger_auto_schema(
        tags=['product'],
        operation_description="Этот эндпоинт позволяет получить список товаров с акциями."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['product'],
        operation_description="Этот эндпоинт позволяет получить список продуктов c акциями."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProductPopularView(generics.ListAPIView):
    serializer_class = ProductShortSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'price', 'promotion', 'description']

    @swagger_auto_schema(
        tags=['product'],
        operation_description="Этот эндпоинт позволяет получить список популярных продуктов "
                              "(только те, у которых есть отзывы)."
    )
    def get_queryset(self):
        # Получаем популярные продукты с аннотациями
        return Product.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')  # Средний рейтинг
        ).filter(
            review_count__gt=0,
            is_active=True
        ).order_by('-avg_rating')  # Сортируем только по avg_rating

    def get(self, request, *args, **kwargs):
        # Используем `get_queryset` для получения данных
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
def get_object_by_value(model, value):
    """Функция для получения объекта модели по значению"""
    if value:
        try:
            # Преобразуем value в верхний регистр для корректного поиска
            return model.objects.get(value=value.upper())  # Ищем в базе по значению в верхнем регистре
        except model.DoesNotExist:
            return None
    return None



class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['product'],
        operation_description="Этот эндпоинт позволяет создать новый продукт.",
        request_body=ProductCreateSerializer,
        responses={
            201: openapi.Response(
                description="Продукт успешно создан",
                schema=ProductCreateSerializer
            ),
            400: openapi.Response(
                description="Ошибка запроса. Возможно, вы указали несуществующие значения для категорий, брендов или цветов.",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Описание ошибки")
                })
            )
        },
        parameters=[
            openapi.Parameter('brand', openapi.IN_BODY, description="Бренд продукта, необходимо указать существующий бренд.",
                              required=True, type=openapi.TYPE_STRING),
            openapi.Parameter('category', openapi.IN_BODY, description="Категория продукта, необходимо указать существующую категорию.",
                              required=True, type=openapi.TYPE_STRING),
            openapi.Parameter('color', openapi.IN_BODY, description="Цвет продукта, необходимо указать существующий цвет.",
                              required=True, type=openapi.TYPE_STRING),
            openapi.Parameter(
                'main_characteristics', openapi.IN_BODY,
                description="Основные характеристики продукта. Должны быть переданы как массив объектов с полями 'label' и 'value'.",
                required=False, type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                    'label': openapi.Schema(type=openapi.TYPE_STRING, description="Название характеристики, например, 'main'"),
                    'value': openapi.Schema(type=openapi.TYPE_STRING, description="Значение характеристики, например, 'grngd'")
                })
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        # Подготовка контекста для сериализатора
        serializer_context = {
            'request': request,
        }

        # Получаем данные из запроса
        request_data = request.data
        brand_value = request_data.get('brand')  # строка, которую отправляет фронт
        category_value = request_data.get('category')  # строка, которую отправляет фронт
        color_value = request_data.get('color')  # строка, которую отправляет фронт

        # Проверка и поиск бренда по значению (value)
        if brand_value:
            brand = get_object_by_value(Brand, brand_value)
            if not brand:
                return Response({"error": f"Brand with the specified value '{brand_value}' does not exist"},
                                status=status.HTTP_400_BAD_REQUEST)
            request_data['brand'] = brand  # заменяем value на сам объект

        # Проверка и поиск категории по значению (value)
        if category_value:
            category = get_object_by_value(Category, category_value)
            if not category:
                return Response({"error": f"Category with the specified value '{category_value}' does not exist"},
                                status=status.HTTP_400_BAD_REQUEST)
            request_data['category'] = category  # заменяем value на сам объект

        # Проверка и поиск цвета по значению (value)
        if color_value:
            color = get_object_by_value(Color, color_value)
            if not color:
                return Response({"error": f"Color with the specified value '{color_value}' does not exist"},
                                status=status.HTTP_400_BAD_REQUEST)
            request_data['color'] = color  # заменяем value на сам объект

        # Создание и валидация продукта с использованием сериализатора
        serializer = ProductCreateSerializer(data=request_data, context=serializer_context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=['review'],
        operation_description="Создать новый комментарий к продукту. Поле `user` берется из токена автоматически.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID продукта'),
                'comments': openapi.Schema(type=openapi.TYPE_STRING, description='Комментарий'),
                'rating': openapi.Schema(type=openapi.TYPE_NUMBER, description='Рейтинг (от 1 до 5)'),
            },
            required=['product', 'rating']
        ),
        responses={
            201: openapi.Response(
                description='Комментарий успешно создан',
                examples={
                    'application/json': {
                        "id": 1,
                        "product": 5,
                        "comments": "Отличный продукт!",
                        "rating": 4.5,
                        "created": "2024-11-29T10:00:00Z",
                        "updated": "2024-11-29T10:00:00Z"
                    }
                }
            ),
            400: "Ошибка валидации данных",
            401: "Аутентификация не выполнена"
        }
    )
    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        # Проверка: один пользователь - один отзыв на продукт
        if Review.objects.filter(user=self.request.user, product=product).exists():
            raise serializers.ValidationError("Вы уже оставили отзыв для этого продукта.")
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=['review'],
        operation_description="Получить, обновить или удалить комментарий по его ID.",
        responses={
            200: openapi.Response('Успешное получение данных', ReviewCreateSerializer),
            400: "Ошибка валидации данных",
            401: "Аутентификация не выполнена",
            403: "Доступ запрещен",
            404: "Комментарий не найден"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Фильтруем, чтобы пользователь видел только свои отзывы
        return Review.objects.filter(user=self.request.user)

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response({"detail": "Комментарий не найден."}, status=status.HTTP_404_NOT_FOUND)
        return super().handle_exception(exc)

class BannerDetailView(APIView):
    def get(self, request, *args, **kwargs):
        banner = Banner.objects.first()
        if banner:
            serializer = BannerSerializer(banner)
            return Response(serializer.data)
        return Response({"detail": "Banner not found"}, status=404)


class ProductArchiveListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=False).order_by('id')
    serializer_class = ProductShortSerializer

    @swagger_auto_schema(
        tags=['product'],
        operation_description="Этот эндпоинт позволяет получить список всех товаров в архиве."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset


