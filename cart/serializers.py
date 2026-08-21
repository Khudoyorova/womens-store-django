from rest_framework import serializers

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_price',
            'quantity',
            'total_price',
            'created_at',
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(
        many=True,
        read_only=True
    )

    total_quantity = serializers.IntegerField(
        read_only=True
    )

    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'items',
            'total_quantity',
            'total_price',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'user',
        ]