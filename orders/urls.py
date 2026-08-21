from django.urls import path

from . import views


app_name = 'orders'


urlpatterns = [
    # Обычные страницы сайта
    path(
        'create/',
        views.order_create,
        name='order_create'
    ),

    path(
        'success/<int:order_id>/',
        views.order_success,
        name='order_success'
    ),

    path(
        'my-orders/',
        views.my_orders,
        name='my_orders'
    ),

    path(
        '<int:order_id>/',
        views.order_detail,
        name='order_detail'
    ),

    # Тестовая оплата на сайте
    path(
        'payment/<int:order_id>/',
        views.payment_page,
        name='payment_page'
    ),

    path(
        'payment/<int:order_id>/process/',
        views.payment_process,
        name='payment_process'
    ),

    path(
        'payment/<int:order_id>/success/',
        views.payment_success,
        name='payment_success'
    ),

    # REST API
    path(
        'api/',
        views.OrderListAPIView.as_view(),
        name='api_orders'
    ),

    path(
        'api/create/',
        views.OrderCreateAPIView.as_view(),
        name='api_order_create'
    ),

    path(
        'api/<int:order_id>/',
        views.OrderDetailAPIView.as_view(),
        name='api_order_detail'
    ),

    path(
        'api/<int:order_id>/pay/',
        views.OrderPaymentAPIView.as_view(),
        name='api_order_payment'
    ),
]