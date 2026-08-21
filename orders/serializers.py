from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'price',
            'quantity',
            'total_price',
        ]

    def get_total_price(self, obj):
        return obj.get_total_price()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    total_price = serializers.SerializerMethodField()

    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )

    class Meta:
        model = Order

        fields = [
            'id',
            'user',
            'first_name',
            'phone',
            'address',
            'status',
            'payment_method',
            'payment_method_display',
            'is_paid',
            'items',
            'total_price',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'user',
            'status',
            'is_paid',
            'created_at',
            'updated_at',
        ]

    def get_total_price(self, obj):
        return obj.get_total_price()