from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'image',
        ]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'category_id',
            'name',
            'slug',
            'description',
            'price',
            'stock',
            'image',
            'is_active',
            'is_new',
            'is_sale',
            'created_at',
        ]