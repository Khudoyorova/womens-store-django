from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import Cart
from .forms import OrderCreateForm
from .models import Order, OrderItem


@login_required
@transaction.atomic
def order_create(request):
    cart = (
        Cart.objects
        .filter(user=request.user)
        .prefetch_related('items__product')
        .first()
    )

    # Проверяем, существует ли корзина и есть ли в ней товары
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

            # Сначала проверяем наличие всех товаров
            for cart_item in cart_items:
                product = cart_item.product

                if cart_item.quantity > product.stock:
                    messages.error(
                        request,
                        (
                            f'Недостаточно товара «{product.name}» '
                            f'на складе. Доступно: {product.stock}.'
                        )
                    )
                    return redirect('cart:cart_detail')

            # Только после проверки создаём заказ
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

                # Уменьшаем остаток товара
                product.stock -= cart_item.quantity
                product.save(update_fields=['stock'])

            # Очищаем корзину
            cart.items.all().delete()

            messages.success(
                request,
                f'Заказ №{order.pk} успешно оформлен.'
            )

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
    # Пользователь сможет открыть только свой заказ
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
    # Получаем только заказы текущего пользователя
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
    # Нельзя посмотреть заказ другого пользователя
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
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