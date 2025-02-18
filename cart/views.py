from decimal import Decimal
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import PermissionDenied

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ApplicationSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Sum, F
from rest_framework.decorators import api_view
from product.models import Product
from .models import Cart, CartItem, Order
from .serializers import (OrderSummarySerializer)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import  CartItem
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework import serializers, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import   CartItem
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
import logging




logger = logging.getLogger(__name__)
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

        cart, _ = Cart.objects.get_or_create(user=user, ordered=False)

        product_id = data.get('product')
        if not product_id:
            return Response({"error": "Product ID is required"}, status=400)

        print(f"Полученный product_id: {product_id}")

        product = get_object_or_404(Product, id=product_id, is_active=True)

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
    def put(self, request, *args, **kwargs):
        """
        Обновление количества товара в корзине.
        """
        # Получаем ID товара и новое количество из данных запроса
        product_id = request.data.get('id')
        new_quantity = int(request.data.get('quantity', 1))

        # Проверка корректности количества
        if new_quantity <= 0:
            return Response({'error': 'Invalid quantity. Quantity must be greater than 0.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Поиск элемента корзины
        try:
            cart_item = get_object_or_404(CartItem, cart__user=request.user, product__id=product_id)
        except Http404:
            return Response({'error': 'Product not found in cart.'}, status=status.HTTP_404_NOT_FOUND)

        # Проверка наличия достаточного количества на складе
        if new_quantity > cart_item.product.quantity:
            return Response({'error': 'Not enough stock available.'}, status=status.HTTP_400_BAD_REQUEST)

        # Определяем цену и скидку в зависимости от роли пользователя
        product = cart_item.product
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
            return Response({'error': 'Calculated price is invalid.'}, status=status.HTTP_400_BAD_REQUEST)

        # Обновляем количество и цену товара в корзине
        cart_item.quantity = new_quantity
        cart_item.price = round(price, 2)  # Сохраняем цену единицы товара с учетом скидки
        cart_item.save()

        # Пересчитываем общую стоимость корзины
        cart = cart_item.cart
        total_quantity = 0
        subtotal = Decimal(0)  # Сумма без скидки
        total_price = Decimal(0)  # Сумма с учетом скидки

        # Пересчитываем все товары в корзине
        for item in cart.items.all():  # Используем related_name 'items'
            # Получаем базовую цену и скидку в зависимости от роли пользователя
            if request.user.role == 'wholesaler':
                item_base_price = item.product.wholesale_price
                item_promotion = item.product.wholesale_promotion
            else:
                item_base_price = item.product.price
                item_promotion = item.product.promotion

            # Рассчитываем цену с учетом скидки
            if item_promotion and 0 <= item_promotion <= 100:
                item_price_with_discount = item_base_price * (1 - Decimal(item_promotion) / Decimal(100))
            else:
                item_price_with_discount = item_base_price

            # Обновляем цену товара в корзине
            item.price = round(item_price_with_discount, 2)
            item.save()

            # Добавляем к общей стоимости
            total_quantity += item.quantity
            subtotal += item_base_price * item.quantity  # Сумма без скидок (базовая цена * количество)
            total_price += item_promotion * item.quantity  # Сумма с учетом скидки (цена с скидкой * количество)

        # Обновляем данные корзины
        cart.total_quantity = total_quantity
        cart.subtotal = round(subtotal, 2)  # Стоимость без скидок
        cart.total_price = round(total_price, 2)  # Стоимость с учетом скидок
        cart.save()

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



def send_order_notification(order, cart):
    subject = "Новый заказ на сайте Homelife"
    items_message = "Список товаров!\n"
    total_quantity = 0
    for item in cart.items.all():
        total_quantity += item.quantity

        product = item.product

        items_message += f"""
    Товар: {product.title}  
    Изображение: {product.image1.url if product.image1 else 'Изображение не доступно'}  
    Количество: {item.quantity}
    Цена: {item.price}c
    Общая стоимость: {item.price * item.quantity}c
    """


    message = f"""
    Заказ №{order.id}
    Дата заказа: {order.created_at}

    Email пользователя: {order.user.email}
    Имя пользователя: {order.user.username}
    Телефон пользователя: {order.user.number}
    Адрес: {order.address}
    """


    if order.by_card:
        message += "Онлайн оплата: Да\n"
    if order.by_cash:
        message += "Оплата наличными через курьера: Да\n"


    message += f"\n{items_message}"


    message += f"""
    Итог:
    Подитоговая сумма без скидки: {cart.subtotal}c
    Итоговая сумма с учетом скидки: {cart.total_price}c
    Количество товаров: {total_quantity}
    """


    admin_email = "homelife.site.kg@gmail.com"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [admin_email],
        fail_silently=False,
    )
    order.application = True
    order.save(update_fields=["application"])



class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=['order'],
        operation_description="Получение данных корзины пользователя",
        responses={
            200: openapi.Response(
                description="Данные корзины",
                examples={
                    'application/json': {
                        "total_quantity": 24,
                        "subtotal": 72000,
                        "totalPrice": 71976
                    }
                },
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_quantity': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                         description='Общее количество товаров в корзине'),
                        'subtotal': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                   description='Общая сумма без учета скидки'),
                        'totalPrice': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                     description='Общая сумма с учетом скидки'),
                    },
                    required=['total_quantity', 'subtotal', 'totalPrice']
                )
            ),
            404: openapi.Response(description="Корзина не найдена"),
            401: openapi.Response(description="Ошибка авторизации"),
            500: openapi.Response(description="Ошибка сервера")
        }
    )
    def get(self, request):
        user = request.user

        is_wholesale = user.role == 'wholesaler'

        cart = Cart.objects.filter(user=user, ordered=False).first()

        if not cart:
            return Response({'error': 'Cart not found'}, status=404)


        total_quantity = cart.items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        subtotal = Decimal(0)
        total_price = Decimal(0)


        for item in cart.items.all():
            product = item.product
            product_price = Decimal(product.price)
            product_promotion = product.promotion

            if is_wholesale:
                product_price = Decimal(product.wholesale_price)
                product_promotion = product.wholesale_promotion

            if product_promotion:
                discounted_price = Decimal(product_promotion)
            else:
                discounted_price = product_price


            subtotal += product_price * item.quantity
            total_price += discounted_price * item.quantity

        return Response({
            "total_quantity": total_quantity,
            "subtotal": int(subtotal),
            "totalPrice": int(total_price),
        })

    @swagger_auto_schema(
        tags=['order'],
        operation_description="Создание заказа для пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['address', 'by_card', 'by_cash'],
            properties={
                'address': openapi.Schema(type=openapi.TYPE_STRING, description='Адрес доставки'),
                'by_card': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Оплата картой'),
                'by_cash': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Оплата наличными'),
            }
        ),
        responses={
            201: openapi.Response(
                description="Заказ успешно создан",
                examples={
                    'application/json': {
                        'message': 'Order created successfully',
                        'order_id': 123,
                        'address': '123 Main Street',
                        'by_card': True,
                        'by_cash': False,
                        'created_at': '14:30:00 14-02-2025'
                    }
                },
            ),
            400: openapi.Response(
                description="Ошибка валидации",
                examples={
                    'application/json': {
                        'error': 'Все поля обязательны'
                    }
                }
            ),
            404: openapi.Response(
                description="Корзина не найдена",
                examples={
                    'application/json': {
                        'error': 'Cart not found'
                    }
                }
            ),
            401: openapi.Response(description="Ошибка авторизации"),
            500: openapi.Response(description="Ошибка сервера")
        }
    )
    def post(self, request):
        user = request.user
        data = request.data

        address = data.get('address')
        by_card = data.get('by_card')
        by_cash = data.get('by_cash')

        if not address or by_card is None or by_cash is None:
            return Response({'error': 'Все поля обязательны'}, status=400)

        if by_card and by_cash:
            return Response({'error': "Only one of 'by_card' or 'by_cash' can be True."}, status=400)

        if not by_card and not by_cash:
            return Response({'error': "At least one of 'by_card' or 'by_cash' must be True."}, status=400)

        # Получаем корзину текущего пользователя
        cart = Cart.objects.filter(user=user, ordered=False).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=404)

        # Создаем заказ
        order = Order.objects.create(
            user=user,
            address=address,
            by_card=by_card,
            by_cash=by_cash,
        )

        # Рассчитываем total_price и total_quantity
        total_price = Decimal('0.00')
        total_quantity = 0

        # Логика для определения роли пользователя (например, через группы)
        user_role = "wholesaler" if user.groups.filter(name="wholesaler").exists() else "retailer"

        for item in cart.items.all():  # Предполагается, что у корзины есть связь с товарами
            if user_role == 'wholesaler':
                price = item.wholesale_price  # Цена для оптовика
            else:
                price = item.retail_price  # Цена для розничного покупателя

            total_price += price * item.quantity
            total_quantity += item.quantity

        # Сохраняем рассчитанные значения в заказ
        order.total_price = total_price
        order.total_quantity = total_quantity
        order.save()

        # Обновляем корзину, чтобы она была отмечена как заказанная
        cart.ordered = True
        cart.save()

        # Отправляем уведомление о заказе
        send_order_notification(order, cart)

        return Response({
            'message': 'Order created successfully',
            'order_id': order.id,
            'address': order.address,
            'by_card': order.by_card,
            'by_cash': order.by_cash,
            'created_at': order.created_at.strftime("%H:%M:%S %d-%m-%Y"),
            'total_price': str(order.total_price),  # Отправляем цену в строковом формате
            'total_quantity': order.total_quantity,
        }, status=201)


class ApplicationView(ListAPIView):
    serializer_class = ApplicationSerializer
    authentication_classes = []  # Отключаем аутентификацию
    permission_classes = []  # Отключаем проверку прав

    def get_queryset(self):
        return Order.objects.filter(application=True)

    def get_serializer_context(self):
        context = super().get_serializer_context()

        # Логика для подсчета total_quantity и total_price
        cart = Cart.objects.filter(ordered=True).order_by('-id').first()

        if cart:
            total_quantity = cart.items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
            total_price = sum(
                (Decimal(item.product.wholesale_price if cart.user.role == 'wholesaler' else item.product.price) *
                 item.quantity) for item in cart.items.all()
            )
        else:
            total_quantity = 0
            total_price = 0

        context["total_quantity"] = total_quantity
        context["total_price"] = int(total_price)
        return context
