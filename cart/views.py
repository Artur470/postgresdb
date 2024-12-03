from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import F, ExpressionWrapper, FloatField
from .models import Cart, CartItem, Order, PaymentMethod
from product.models import Product
from .serializers import CartItemsSerializer, OrderSerializer
from django.db.models import Sum, F
from .serializers import CartItemsSerializer, OrderSerializer
from decimal import Decimal
from rest_framework_simplejwt.authentication import JWTAuthentication

class CartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=['cart'],
        operation_description="Получить список товаров в корзине пользователя.",
        responses={  # Описание возможных ответов
            200: openapi.Response(
                description="Список товаров в корзине пользователя",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'items': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'cart_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID корзины"),
                                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID товара"),
                                'title': openapi.Schema(type=openapi.TYPE_STRING, description="Название товара"),
                                'image': openapi.Schema(type=openapi.TYPE_STRING, description="URL изображения товара"),
                                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description="Количество товара"),
                                'price': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Цена товара"),
                            },
                        )),
                        'total_quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description="Общее количество товаров в корзине"),
                        'subtotal': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Сумма без учета скидки"),
                        'totalPrice': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Итоговая стоимость товаров с учетом скидки"),
                    }
                ),
            ),
            404: openapi.Response(
                description="Корзина не найдена",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
                )
            ),
        },
    )
    def get(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user, ordered=False).first()

        if not cart:
            return Response({'error': 'Cart not found'}, status=404)

        # Получаем товары в корзине
        queryset = CartItem.objects.filter(cart=cart)

        # Переменные для подсчета
        total_quantity = 0
        subtotal = Decimal(0)  # Общая сумма без скидки
        total_price = Decimal(0)  # Итоговая стоимость с учетом скидки

        # Обрабатываем каждый элемент корзины
        for item in queryset:
            product = item.product
            product_price = Decimal(product.price)  # Обычная цена товара
            product_promotion = product.promotion  # Скидка товара, если есть

            # Рассчитываем цену с учетом скидки
            if product_promotion:
                discounted_price = Decimal(product.promotion)  # Цена товара с учетом скидки
            else:
                discounted_price = product_price  # Если скидки нет, используем обычную цену

            # Обновляем итоговые значения
            total_quantity += item.quantity
            subtotal += product_price * item.quantity  # Сумма без скидки
            total_price += discounted_price * item.quantity  # Итоговая сумма с учетом скидки

        # Сохраняем обновленные значения корзины
        cart.total_quantity = total_quantity
        cart.subtotal = subtotal
        cart.total_price = total_price
        cart.save()

        # Сериализуем товары для ответа
        serializer = CartItemsSerializer(queryset, many=True)

        # Формируем ответ
        return Response({
            'items': serializer.data,
            'total_quantity': total_quantity,
            'subtotal': float(subtotal),  # Преобразуем Decimal в float для JSON ответа
            'totalPrice': float(total_price),
        })
    def post(self, request):
        data = request.data
        user = request.user
        # Получаем корзину пользователя (или создаем новую, если она не существует)
        cart, _ = Cart.objects.get_or_create(user=user, ordered=False)

        # Получаем товар, который был добавлен
        product = get_object_or_404(Product, id=data.get('product'))
        quantity = int(data.get('quantity', 1))

        # Проверка на корректность количества
        if quantity <= 0:
            return Response({'error': 'Quantity must be greater than 0'}, status=400)

        if quantity > product.quantity:
            return Response({'error': 'Not enough stock available'}, status=400)

        # Рассчитываем цену с учетом промоакции (если она есть)
        price = product.price
        promotion = product.promotion or 0
        if promotion > 0:
            price *= (1 - promotion / 100)

        # Добавляем товар в корзину без уменьшения количества на складе
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'price': price, 'quantity': quantity, 'user': user}
        )

        if not created:
            # Обновляем существующий CartItem
            cart_item.quantity += quantity
            cart_item.price = price * cart_item.quantity
            cart_item.save()

        # Обновляем общую стоимость корзины
        cart.total_price = sum(item.price * item.quantity for item in CartItem.objects.filter(cart=cart))
        cart.save()

        return Response({'success': 'Item added to your cart'})

    @swagger_auto_schema(
        tags=['cart'],
        operation_description="Обновить количество товара в корзине.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID товара в корзине"),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description="Новое количество товара", example=1),
            },
            required=['id', 'quantity']
        ),
        responses={
            200: openapi.Response(
                description="Товар обновлен успешно",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'items': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'cart_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID корзины"),
                                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID товара"),
                                'title': openapi.Schema(type=openapi.TYPE_STRING, description="Название товара"),
                                'image': openapi.Schema(type=openapi.TYPE_STRING, description="URL изображения товара"),
                                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description="Количество товара"),
                                'price': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT,
                                                        description="Цена товара"),
                            },
                        )),
                        'total_quantity': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                         description="Общее количество товаров в корзине"),
                        'subtotal': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT,
                                                   description="Сумма без учета скидки"),
                        'totalPrice': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT,
                                                     description="Итоговая стоимость товаров с учетом скидки"),
                        'success': openapi.Schema(type=openapi.TYPE_STRING,
                                                  description="Сообщение об успешном обновлении товара"),
                    }
                ),
            ),
            400: openapi.Response(
                description="Неверное количество товара",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING, description="Ошибка")}
                )
            ),
            404: openapi.Response(
                description="Товар не найден",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING, description="Ошибка")}
                )
            ),
        }
    )
    def put(self, request):
        # Получаем ID товара и новое количество из данных запроса
        product_id = request.data.get('id')
        new_quantity = int(request.data.get('quantity', 1))


        if new_quantity <= 0:
            return Response({'error': 'Invalid quantity'}, status=400)

        try:
            cart_item = get_object_or_404(CartItem, cart__user=request.user, product__id=product_id)
        except NotFound:
            return Response({'error': 'Product not found in cart'}, status=404)

        # Проверка, есть ли достаточно товара на складе
        if new_quantity > cart_item.product.quantity:
            return Response({'error': 'Not enough stock'}, status=400)


        product = cart_item.product
        price = product.price * (1 - (Decimal(product.promotion or 0) / Decimal(100)))


        cart_item.quantity = new_quantity
        cart_item.price = price * Decimal(new_quantity)
        cart_item.save()

        # Пересчитываем общую стоимость корзины
        self.update_cart_totals(cart_item.cart)

        return Response({
            'items': CartItemsSerializer(cart_item.cart.items.all(), many=True).data,
            'total_quantity': cart_item.cart.total_quantity,
            'subtotal': cart_item.cart.subtotal,
            'totalPrice': cart_item.cart.total_price,
            'success': 'Product updated'
        })
    @swagger_auto_schema(
        tags=['cart'],
        operation_description="Удалить товар из корзины по ID товара.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID товара для удаления из корзины"),
            },
            required=['id']
        ),
        responses={
            204: openapi.Response(
                description="Товар успешно удален из корзины",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'items': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'cart_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID корзины"),
                                    'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID товара"),
                                    'title': openapi.Schema(type=openapi.TYPE_STRING, description="Название товара"),
                                    'image': openapi.Schema(type=openapi.TYPE_STRING,
                                                            description="URL изображения товара"),
                                    'quantity': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                               description="Количество товара"),
                                    'price': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT,
                                                            description="Цена товара"),
                                },
                            )
                        ),
                        'total_quantity': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                         description="Общее количество товаров в корзине"),
                        'subtotal': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT,
                                                   description="Сумма без учета скидки"),
                        'totalPrice': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT,
                                                     description="Итоговая стоимость товаров с учетом скидки"),
                        'success': openapi.Schema(type=openapi.TYPE_STRING,
                                                  description="Сообщение об успешном удалении товара"),
                    }
                )
            ),
            400: openapi.Response(
                description="Не указан ID товара или некорректный запрос",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING, description="Ошибка")}
                )
            ),
            404: openapi.Response(
                description="Товар не найден в корзине",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING, description="Ошибка")}
                )
            ),
        }
    )
    def delete(self, request):
        product_id = request.data.get('id')
        if not product_id:
            return Response({'error': 'Product ID not provided'}, status=400)

        cart_items = CartItem.objects.filter(product__id=product_id, cart__user=request.user)

        if not cart_items.exists():
            return Response({'error': 'No CartItem found for this product in your cart'}, status=404)

        for cart_item in cart_items:
            cart_item.delete()

        # Обновляем общую стоимость корзины
        cart = Cart.objects.get(user=request.user, ordered=False)
        self.update_cart_totals(cart)

        return Response({
            'items': CartItemsSerializer(cart.items.all(), many=True).data,
            'total_quantity': cart.total_quantity,
            'subtotal': cart.subtotal,
            'totalPrice': cart.total_price,
            'success': 'Items removed from cart'
        }, status=204)

    def update_cart_totals(self, cart):
        """Метод для пересчета итоговых значений корзины"""
        cart.total_price = sum(item.price * item.quantity for item in cart.items.all())
        cart.total_quantity = sum(item.quantity for item in cart.items.all())
        cart.subtotal = sum(item.product.price * item.quantity for item in cart.items.all())
        cart.save()

class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['order'],
        operation_description="Оформить заказ. Введите адрес и способ оплаты: 1 - наличные, 2 - карта.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'address': openapi.Schema(type=openapi.TYPE_STRING, description="Адрес доставки"),
                'payment_method': openapi.Schema(type=openapi.TYPE_INTEGER, description="Способ оплаты (1 - наличные, 2 - карта)")
            },
            required=['address', 'payment_method']
        ),
        responses={
            201: openapi.Response(description="Заказ создан"),
            400: openapi.Response(description="Ошибка создания заказа")
        }
    )
    def post(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user, ordered=False).first()

        if not cart:
            return Response({'error': 'Cart not found'}, status=400)

        # Уменьшаем количество товара на складе при оформлении заказа
        for cart_item in cart.cartitem_set.all():
            product = cart_item.product
            product.quantity -= cart_item.quantity
            product.save()

        order = Order.objects.create(
            user=user,
            address=request.data['address'],
            payment_method=PaymentMethod.objects.get(id=request.data['payment_method']),
            cart=cart
        )

        cart.ordered = True
        cart.save()

        return Response(OrderSerializer(order).data, status=201)
