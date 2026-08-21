from django.conf import settings
from django.db import models

from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличными при получении'),
        ('card', 'Банковская карта'),
        ('click', 'Click'),
        ('payme', 'Payme'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь'
    )

    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )

    phone = models.CharField(
        max_length=30,
        verbose_name='Телефон'
    )

    address = models.TextField(
        verbose_name='Адрес доставки'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash',
        verbose_name='Способ оплаты'
    )

    is_paid = models.BooleanField(
        default=False,
        verbose_name='Оплачено'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ №{self.pk} — {self.user.username}'

    def get_total_price(self):
        return sum(
            item.get_total_price()
            for item in self.items.all()
        )


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='Товар'
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена'
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Товар заказа'
        verbose_name_plural = 'Товары заказа'

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'

    def get_total_price(self):
        return self.price * self.quantity