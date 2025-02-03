from django.urls import path
from cart.views import CartView,OrderView

urlpatterns = [
    path('carts/', CartView.as_view(), name='cart_list'),  # Получить список товаров в корзине
    path('order/', OrderView.as_view(), name='create_order'),

]
