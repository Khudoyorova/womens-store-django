from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name='Slug'
    )

    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'category_detail',
            kwargs={'slug': self.slug}
        )


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория'
    )

    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        verbose_name='Slug'
    )

    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена'
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )

    stock = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    is_new = models.BooleanField(
        default=False,
        verbose_name='Новинка'
    )

    is_sale = models.BooleanField(
        default=False,
        verbose_name='Акция'
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
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'product_detail',
            kwargs={'slug': self.slug}
        )


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Товар'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Пользователь'
    )

    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ],
        verbose_name='Оценка'
    )

    text = models.TextField(
        verbose_name='Текст отзыва'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

        constraints = [
            models.UniqueConstraint(
                fields=['product', 'user'],
                name='unique_product_review_by_user'
            )
        ]

    def __str__(self):
        return f'{self.user} — {self.product.name}'