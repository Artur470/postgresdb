from django.urls import path
from cart.views import CartView, CreateOrderView, ApplicationView  # Убедитесь, что оба представления импортированы правильно
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('carts/', CartView.as_view(), name='cart_list'),  # Получить список товаров в корзине
    path('order/', CreateOrderView.as_view(), name='create_order'),  # Создать новый заказ
    path('applications/', ApplicationView.as_view(), name='applications'),  # Создать новый заказ
]
