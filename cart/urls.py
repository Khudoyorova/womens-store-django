from django.urls import path

from . import views


app_name = 'cart'


urlpatterns = [
    path(
        '',
        views.cart_detail,
        name='cart_detail'
    ),

    path(
        'add/<int:product_id>/',
        views.cart_add,
        name='cart_add'
    ),

    path(
        'update/<int:item_id>/',
        views.cart_update,
        name='cart_update'
    ),

    path(
        'remove/<int:item_id>/',
        views.cart_remove,
        name='cart_remove'
    ),

    path(
        'clear/',
        views.cart_clear,
        name='cart_clear'
    ),

    path(
        'api/',
        views.CartAPIView.as_view(),
        name='api_cart'
    ),

    path(
        'api/items/add/',
        views.CartItemAddAPIView.as_view(),
        name='api_cart_item_add'
    ),

    path(
        'api/items/<int:item_id>/',
        views.CartItemDetailAPIView.as_view(),
        name='api_cart_item_detail'
    ),
]