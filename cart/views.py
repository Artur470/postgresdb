from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import Http404
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
        # Проверка роли через поле `role` у пользователя
        is_wholesale = user.role == 'wholesaler'  # Проверка, является ли пользователь оптовиком

        # Получаем корзину пользователя
        cart = Cart.objects.filter(user=user, ordered=False).first()

        if not cart:
            return Response({'error': 'Cart not found'}, status=404)

        # Получаем товары в корзине и оптимизируем запросы
        queryset = CartItem.objects.filter(cart=cart).select_related('product')

        # Переменные для подсчета
        total_quantity = sum(item.quantity for item in queryset)
        subtotal = Decimal(0)  # Общая сумма без скидки
        total_price = Decimal(0)  # Итоговая стоимость с учетом скидки
        item_data_list = []  # Список для хранения данных о каждом товаре

        # Обрабатываем каждый элемент корзины
        for item in queryset:
            product = item.product
            product_price = Decimal(product.price)  # Обычная цена товара
            product_promotion = product.promotion  # Скидка товара, если есть

            # Если пользователь оптовик, используем оптовую цену и скидку
            if is_wholesale:
                product_price = Decimal(product.wholesale_price)  # Оптовая цена
                product_promotion = product.wholesale_promotion  # Оптовая скидка

            # Рассчитываем цену с учетом скидки
            if product_promotion:
                discounted_price = Decimal(product_promotion)  # Цена товара с учетом скидки
                price_to_return = discounted_price  # Цена с учетом скидки
            else:
                discounted_price = product_price  # Если скидки нет, используем обычную цену
                price_to_return = product_price  # Цена без скидки

            # Обновляем итоговые значения
            subtotal += product_price * item.quantity  # Сумма без скидки
            total_price += discounted_price * item.quantity  # Итоговая сумма с учетом скидки

            # Включаем цену с учетом скидки в сериализатор
            item_data = {
                'cart_id': cart.id,
                'product_id': product.id,
                'title': product.title,
                'image': product.image1.url if product.image1 else None,
                # Используйте image1 или другое поле изображения
                'quantity': item.quantity,
                'price': int(price_to_return),  # Преобразуем цену в float для JSON
            }
            item_data_list.append(item_data)

        # Сериализуем товары для ответа
        return Response({
            'items': item_data_list,
            'total_quantity': total_quantity,
            'subtotal': int(subtotal),  # Преобразуем Decimal в float для JSON ответа
            'totalPrice': int(total_price),
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
        """
        Обновление количества товара в корзине.
        """
        # Получаем ID товара и новое количество из данных запроса
        product_id = request.data.get('id')
        new_quantity = int(request.data.get('quantity', 1))

        # Проверка корректности количества
        if new_quantity <= 0:
            return Response({'error': 'Invalid quantity. Quantity must be greater than 0.'}, status=400)

        # Поиск элемента корзины
        try:
            cart_item = get_object_or_404(CartItem, cart__user=request.user, product__id=product_id)
        except NotFound:
            return Response({'error': 'Product not found in cart.'}, status=404)

        # Проверка наличия достаточного количества на складе
        if new_quantity > cart_item.product.quantity:
            return Response({'error': 'Not enough stock available.'}, status=400)

        product = cart_item.product

        # Определяем цену и скидку в зависимости от роли пользователя
        if request.user.role == 'wholesaler':  # Если пользователь — оптовик
            base_price = product.wholesale_price
            promotion = product.wholesale_promotion
        else:  # Если пользователь — обычный клиент
            base_price = product.price
            promotion = product.promotion

        # Рассчитываем цену с учетом скидки
        if promotion and 0 <= promotion <= 100:
            price = base_price * (1 - (Decimal(promotion) / Decimal(100)))  # Применяем скидку
        else:
            price = base_price  # Если скидки нет или она некорректна, используем базовую цену

        # Проверка на отрицательную цену
        if price < 0:
            return Response({'error': 'Calculated price is invalid.'}, status=400)

        # Обновляем количество и цену товара в корзине
        cart_item.quantity = new_quantity
        cart_item.price = round(price, 2)  # Сохраняем цену единицы товара с учетом скидки
        cart_item.save()

        # Отладочные сообщения
        print(f"Updated cart_item: {cart_item.product.title}, Quantity: {cart_item.quantity}, Price: {cart_item.price}")

        # Пересчитываем общую стоимость корзины
        cart = cart_item.cart
        total_quantity = 0
        subtotal = Decimal(0)  # Сумма без скидок
        total_price = Decimal(0)  # Сумма с учетом скидок

        for item in cart.items.all():
            # Получаем базовую цену и скидку в зависимости от роли пользователя
            if request.user.role == 'wholesaler':
                item_base_price = item.product.wholesale_price
                item_promotion = item.product.wholesale_promotion
            else:
                item_base_price = item.product.price
                item_promotion = item.product.promotion

            # Рассчитываем цену с учетом скидки
            if item_promotion and 0 <= item_promotion <= 100:
                item_price = item_base_price * (1 - Decimal(item_promotion) / Decimal(100))  # Цена со скидкой
            else:
                item_price = item_base_price  # Если скидки нет, используем базовую цену

            # Обновляем цену товара в корзине
            item.price = round(item_price, 2)
            item.save()

            # Добавляем к общей стоимости
            total_quantity += item.quantity
            subtotal += item_base_price * item.quantity  # Сумма без скидки
            total_price += item_price * item.quantity  # Сумма с учетом скидки

            # Отладочные сообщения
            print(f"Updated item: {item.product.title}, Quantity: {item.quantity}, Price: {item.price}")

        # Обновляем данные корзины
        cart.total_quantity = total_quantity
        cart.subtotal = round(subtotal, 2)  # Стоимость без скидок
        cart.total_price = round(total_price, 2)  # Стоимость с учетом скидок
        cart.save()

        # Отладочные сообщения
        print(
            f"Updated cart: Total Quantity: {cart.total_quantity}, Subtotal: {cart.subtotal}, Total Price: {cart.total_price}")

        # Возвращаем обновленные данные корзины
        return Response({
            'items': CartItemsSerializer(cart.items.all(), many=True, context={'request': request}).data,
            'total_quantity': cart.total_quantity,
            'subtotal': round(cart.subtotal, 2),  # Стоимость без скидок
            'totalPrice': round(cart.total_price, 2),  # Стоимость с учетом скидок
            'success': 'Product updated successfully'
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
                                    'cart_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'product_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'title': openapi.Schema(type=openapi.TYPE_STRING),
                                    'image': openapi.Schema(type=openapi.TYPE_STRING),
                                    'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'price': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                                }
                            )
                        ),
                        'total_quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'subtotal': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                        'totalPrice': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                    }
                ),
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
    def delete(self, request):
        data = request.data
        user = request.user
        product_id = data.get('id')

        # Получаем корзину пользователя
        cart = Cart.objects.filter(user=user, ordered=False).first()

        if not cart:
            return Response({'error': 'Cart not found'}, status=404)

        try:
            # Находим товар в корзине по product_id
            cart_item = CartItem.objects.get(cart=cart, product__id=product_id)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        # Пересчитываем общую стоимость корзины после удаления товара
        cart.total_price = sum(item.price * item.quantity for item in CartItem.objects.filter(cart=cart))
        cart.save()

        return Response({
            'items': CartItemsSerializer(cart.items.all(), many=True).data,
            'total_quantity': cart.total_quantity,
            'subtotal': cart.subtotal,
            'totalPrice': cart.total_price,
        }, status=204)

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
