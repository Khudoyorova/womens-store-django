from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .serializers import OrderSerializer


# =========================================================
# ОБЫЧНЫЕ DJANGO VIEWS
# =========================================================

@login_required
@transaction.atomic
def order_create(request):
    cart = (
        Cart.objects
        .filter(user=request.user)
        .prefetch_related('items__product')
        .first()
    )

    if not cart or not cart.items.exists():
        messages.warning(
            request,
            'Ваша корзина пуста.'
        )
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            cart_items = list(
                cart.items.select_related('product')
            )

            # Проверяем остатки товаров
            for cart_item in cart_items:
                product = cart_item.product

                if cart_item.quantity > product.stock:
                    messages.error(
                        request,
                        (
                            f'Недостаточно товара «{product.name}» '
                            f'на складе. '
                            f'Доступно: {product.stock}.'
                        )
                    )

                    return redirect(
                        'cart:cart_detail'
                    )

            # Создаём заказ
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            # Переносим товары из корзины в заказ
            for cart_item in cart_items:
                product = cart_item.product

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=cart_item.quantity
                )

                product.stock -= cart_item.quantity

                product.save(
                    update_fields=['stock']
                )

            # Очищаем корзину
            cart.items.all().delete()

            messages.success(
                request,
                f'Заказ №{order.pk} успешно оформлен.'
            )

            # Онлайн-оплата
            if order.payment_method in [
                'card',
                'click',
                'payme',
            ]:
                return redirect(
                    'orders:payment_page',
                    order_id=order.pk
                )

            # Наличная оплата
            return redirect(
                'orders:order_success',
                order_id=order.pk
            )

    else:
        form = OrderCreateForm(
            initial={
                'first_name': (
                    request.user.first_name
                    or request.user.username
                ),
            }
        )

    context = {
        'form': form,
        'cart': cart,
    }

    return render(
        request,
        'orders/order_create.html',
        context
    )


@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order,
        pk=order_id,
        user=request.user
    )

    return render(
        request,
        'orders/order_success.html',
        {
            'order': order,
            'order_id': order.pk,
        }
    )


@login_required
def my_orders(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related('items__product')
        .order_by('-created_at')
    )

    return render(
        request,
        'orders/my_orders.html',
        {
            'orders': orders,
        }
    )


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related(
            'items__product'
        ),
        pk=order_id,
        user=request.user
    )

    return render(
        request,
        'orders/order_detail.html',
        {
            'order': order,
        }
    )


# =========================================================
# ТЕСТОВАЯ ОПЛАТА
# =========================================================

@login_required
def payment_page(request, order_id):
    order = get_object_or_404(
        Order,
        pk=order_id,
        user=request.user
    )

    if order.is_paid:
        return redirect(
            'orders:payment_success',
            order_id=order.pk
        )

    return render(
        request,
        'orders/payment.html',
        {
            'order': order,
        }
    )


@login_required
@transaction.atomic
def payment_process(request, order_id):
    order = get_object_or_404(
        Order,
        pk=order_id,
        user=request.user
    )

    if request.method != 'POST':
        return redirect(
            'orders:payment_page',
            order_id=order.pk
        )

    if not order.is_paid:
        order.is_paid = True

        order.save(
            update_fields=['is_paid']
        )

    return redirect(
        'orders:payment_success',
        order_id=order.pk
    )


@login_required
def payment_success(request, order_id):
    order = get_object_or_404(
        Order,
        pk=order_id,
        user=request.user,
        is_paid=True
    )

    return render(
        request,
        'orders/payment_success.html',
        {
            'order': order,
        }
    )


# =========================================================
# REST API
# =========================================================

class OrderListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = (
            Order.objects
            .filter(user=request.user)
            .prefetch_related('items__product')
            .order_by('-created_at')
        )

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(
            Order.objects.prefetch_related(
                'items__product'
            ),
            pk=order_id,
            user=request.user
        )

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        cart = (
            Cart.objects
            .filter(user=request.user)
            .prefetch_related('items__product')
            .first()
        )

        if not cart or not cart.items.exists():
            return Response(
                {
                    'detail': 'Ваша корзина пуста.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        first_name = request.data.get('first_name')
        phone = request.data.get('phone')
        address = request.data.get('address')

        payment_method = request.data.get(
            'payment_method',
            'cash'
        )

        valid_payment_methods = [
            choice[0]
            for choice in Order.PAYMENT_METHOD_CHOICES
        ]

        if payment_method not in valid_payment_methods:
            return Response(
                {
                    'detail': 'Неверный способ оплаты.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not first_name or not phone or not address:
            return Response(
                {
                    'detail': (
                        'Укажите first_name, '
                        'phone и address.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = list(
            cart.items.select_related('product')
        )

        for cart_item in cart_items:
            product = cart_item.product

            if cart_item.quantity > product.stock:
                return Response(
                    {
                        'detail': (
                            f'Недостаточно товара '
                            f'«{product.name}». '
                            f'Доступно: {product.stock}.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            phone=phone,
            address=address,
            payment_method=payment_method
        )

        for cart_item in cart_items:
            product = cart_item.product

            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=cart_item.quantity
            )

            product.stock -= cart_item.quantity

            product.save(
                update_fields=['stock']
            )

        cart.items.all().delete()

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )



class OrderPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):
        order = get_object_or_404(
            Order,
            pk=order_id,
            user=request.user
        )

        if order.is_paid:
            return Response(
                {
                    'detail': 'Заказ уже оплачен.',
                    'order_id': order.id,
                    'is_paid': True,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.payment_method == 'cash':
            return Response(
                {
                    'detail': (
                        'Для оплаты наличными онлайн-оплата '
                        'не требуется.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        order.is_paid = True
        order.save(
            update_fields=['is_paid']
        )

        return Response(
            {
                'detail': 'Оплата прошла успешно.',
                'order_id': order.id,
                'payment_method': order.payment_method,
                'payment_method_display': (
                    order.get_payment_method_display()
                ),
                'is_paid': order.is_paid,
                'total_price': order.get_total_price(),
            },
            status=status.HTTP_200_OK
        )