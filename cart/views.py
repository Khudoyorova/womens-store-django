from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_items = cart.items.select_related(
        'product',
        'product__category'
    )

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }

    return render(
        request,
        'cart/cart_detail.html',
        context
    )


@login_required
@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    if product.stock <= 0:
        messages.error(
            request,
            'Товара нет в наличии.'
        )
        return redirect(
            'product_detail',
            slug=product.slug
        )

    try:
        quantity = int(
            request.POST.get('quantity', 1)
        )
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 0}
    )

    new_quantity = cart_item.quantity + quantity

    if new_quantity > product.stock:
        new_quantity = product.stock

        messages.warning(
            request,
            'Добавлено максимально доступное количество.'
        )
    else:
        messages.success(
            request,
            'Товар добавлен в корзину.'
        )

    cart_item.quantity = new_quantity
    cart_item.save()

    return redirect('cart:cart_detail')


@login_required
@require_POST
def cart_update(request, item_id):
    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )

    try:
        quantity = int(
            request.POST.get('quantity', 1)
        )
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        cart_item.delete()

        messages.success(
            request,
            'Товар удалён из корзины.'
        )

        return redirect('cart:cart_detail')

    if quantity > cart_item.product.stock:
        quantity = cart_item.product.stock

        messages.warning(
            request,
            'Установлено максимально доступное количество.'
        )

    cart_item.quantity = quantity
    cart_item.save()

    messages.success(
        request,
        'Количество товара изменено.'
    )

    return redirect('cart:cart_detail')


@login_required
@require_POST
def cart_remove(request, item_id):
    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )

    cart_item.delete()

    messages.success(
        request,
        'Товар удалён из корзины.'
    )

    return redirect('cart:cart_detail')


@login_required
@require_POST
def cart_clear(request):
    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    cart.items.all().delete()

    messages.success(
        request,
        'Корзина очищена.'
    )

    return redirect('cart:cart_detail')


class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        serializer = CartSerializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CartItemAddAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True
        )

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {
                    'detail': 'Количество должно быть числом.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity < 1:
            return Response(
                {
                    'detail': 'Количество должно быть больше 0.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if product.stock <= 0:
            return Response(
                {
                    'detail': 'Товара нет в наличии.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': 0
            }
        )

        new_quantity = cart_item.quantity + quantity

        if new_quantity > product.stock:
            new_quantity = product.stock

        cart_item.quantity = new_quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)

        if item_created:
            response_status = status.HTTP_201_CREATED
        else:
            response_status = status.HTTP_200_OK

        return Response(
            serializer.data,
            status=response_status
        )


class CartItemDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        cart = get_object_or_404(
            Cart,
            user=request.user
        )

        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart=cart
        )

        quantity = request.data.get('quantity')

        if quantity is None:
            return Response(
                {
                    'detail': 'Укажите quantity.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {
                    'detail': 'Количество должно быть числом.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity <= 0:
            cart_item.delete()

            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

        if quantity > cart_item.product.stock:
            quantity = cart_item.product.stock

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def delete(self, request, item_id):
        cart = get_object_or_404(
            Cart,
            user=request.user
        )

        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart=cart
        )

        cart_item.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )