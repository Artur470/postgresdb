from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from .models import Cart, CartItem, Order


class CartSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()  # Итоговая цена корзины
    total_quantity = serializers.SerializerMethodField()  # Общее количество товаров
    cart_items = serializers.SerializerMethodField()  # Детализация товаров в корзине
    subtotal = serializers.SerializerMethodField()  # Стоимость до применения скидок

    class Meta:
        model = Cart
        fields = ['id', 'total_price', 'total_quantity', 'cart_items', 'subtotal']

    def get_total_price(self, obj):
        """Рассчитывает общую цену корзины с учетом скидок и роли пользователя."""
        total_price = Decimal('0.00')
        user = self.context.get('request').user if self.context.get('request') else None

        if user:
            for item in obj.cartitem_set.select_related('product').all():
                product_price = self.calculate_product_price(item.product, user)  # Цена с учетом скидки
                total_price += product_price * item.quantity  # Умножаем на количество товара

        return round(total_price, 2)  # Округляем до 2 знаков

    def get_subtotal(self, obj):
        """Рассчитывает стоимость корзины без учета скидок (только стандартные цены)."""
        subtotal = Decimal('0.00')
        user = self.context.get('request').user if self.context.get('request') else None

        if user:
            for item in obj.cartitem_set.select_related('product').all():
                product_price = item.product.price or Decimal('0.00')  # Используем базовую цену без скидки
                subtotal += product_price * item.quantity  # Умножаем на количество товара

        return round(subtotal, 2)  # Округляем до 2 знаков

    def get_total_quantity(self, obj):
        """Возвращает общее количество всех товаров в корзине."""
        return obj.cartitem_set.aggregate(total=Sum('quantity'))['total'] or 0

    def get_cart_items(self, obj):
        """Собирает детализированную информацию о товарах в корзине."""
        user = self.context.get('request').user if self.context.get('request') else None
        items = obj.cartitem_set.select_related('product').all()
        cart_items_data = []

        for item in items:
            product_price = self.calculate_product_price(item.product, user)
            cart_items_data.append({
                'cart_id': obj.id,
                'product_id': item.product.id,
                'title': item.product.title,
                'image': item.product.image.url if item.product.image else None,
                'quantity': item.quantity,
                'price': round(product_price, 2)  # Цена с округлением до 2 знаков
            })

        return cart_items_data

    def calculate_product_price(self, product, user):
        """Вычисляет цену товара с учетом роли пользователя и скидки."""
        if not user:
            return Decimal('0.00')  # Если пользователь не авторизован

        # Если пользователь - оптовик
        if user.role == 'wholesaler':
            base_price = product.wholesale_price or Decimal('0.00')  # Оптовая цена товара
            promotion = product.wholesale_promotion  # Скидка для оптовиков
        else:
            base_price = product.price or Decimal('0.00')  # Обычная цена товара
            promotion = product.promotion  # Скидка для обычных покупателей

        # Применяем скидку, если она есть (в процентах)
        if promotion and 0 <= promotion <= 100:
            product_price = base_price * (1 - Decimal(promotion) / Decimal(100))  # Цена с учетом скидки
        else:
            product_price = base_price  # Если скидки нет, берем базовую цену товара

        return round(product_price, 2)  # Округляем до 2 знаков


class CartItemsSerializer(serializers.ModelSerializer):
    cart_id = serializers.IntegerField(source='cart.id', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    title = serializers.CharField(source='product.title', read_only=True)
    image = serializers.SerializerMethodField()  # Изображение товара
    quantity = serializers.IntegerField()
    price = serializers.SerializerMethodField()  # Цена товара

    class Meta:
        model = CartItem
        fields = ['cart_id', 'product_id', 'title', 'image', 'quantity', 'price']

    def get_image(self, obj):
        """Возвращает URL изображения товара, если доступно."""
        return self.get_product_image(obj.product)

    def get_price(self, obj):
        """Вычисляет цену за единицу товара с учетом роли пользователя и количества товара."""
        user = self.context.get('request').user if self.context.get('request') else None
        if user:
            price = self.calculate_product_price(obj.product, user)
            # Пересчитываем цену с учетом количества
            return round(price * obj.quantity, 2)  # Округляем до 2 знаков
        return Decimal('0.00')  # Если пользователь не авторизован, цена 0.00

    def calculate_product_price(self, product, user):
        """Определяет цену товара для оптовиков или обычных пользователей."""
        if not user:
            return Decimal('0.00')  # Если пользователь не авторизован

        if user.role == 'wholesaler':
            return product.wholesale_promotion or product.wholesale_price or Decimal('0.00')
        return product.promotion or product.price or Decimal('0.00')

    def get_product_image(self, product):
        """Возвращает первое доступное изображение товара."""
        if product.image1:
            return product.image1.url
        if product.image2:
            return product.image2.url
        if product.image3:
            return product.image3.url
        return None

# class PaymentMethodSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PaymentMethod
#         fields = ['id', 'name']

class OrderSerializer(serializers.ModelSerializer):


    class Meta:
        model = Order
        fields = ['user', 'cart', 'total_price', 'address', 'by_cash', 'by_card']

    def create(self, validated_data):
        cart = validated_data.get('cart')

        # Проверка на пустую корзину
        if cart.cartitem_set.count() == 0:
            raise serializers.ValidationError("Корзина пуста. Невозможно создать заказ.")

        order = Order.objects.create(**validated_data)

        # Уменьшение количества товаров на складе при создании заказа
        for item in order.cart.cartitem_set.all():
            item.product.quantity -= item.quantity
            item.product.save()

        order.clear_user_cart()  # Очистка корзины пользователя после создания заказа
        order.send_order_email()  # Отправка уведомления на почту

        return order
