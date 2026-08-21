from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .forms import ReviewForm
from .models import Category, Product
from .serializers import ProductSerializer, CategorySerializer

from .permissions import IsAdminOrReadOnly


def home(request):
    categories = Category.objects.filter(
        is_active=True
    )

    products = Product.objects.filter(
        is_active=True,
        category__is_active=True
    ).select_related('category')

    context = {
        'categories': categories,
        'products': products,
    }

    return render(request, 'home.html', context)


def category_detail(request, slug):
    category = get_object_or_404(
        Category,
        slug=slug,
        is_active=True
    )

    categories = Category.objects.filter(
        is_active=True
    )

    products = Product.objects.filter(
        category=category,
        is_active=True
    ).select_related('category')

    context = {
        'category': category,
        'categories': categories,
        'products': products,
    }

    return render(
        request,
        'products/category_detail.html',
        context
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category'),
        slug=slug,
        is_active=True,
        category__is_active=True
    )

    reviews = product.reviews.select_related('user').all()

    review_form = ReviewForm()

    if request.method == 'POST':

        if not request.user.is_authenticated:
            messages.warning(
                request,
                'Чтобы оставить отзыв, сначала войдите в аккаунт.'
            )
            return redirect('users:login')

        if product.reviews.filter(user=request.user).exists():
            messages.warning(
                request,
                'Вы уже оставляли отзыв к этому товару.'
            )
            return redirect(product.get_absolute_url())

        review_form = ReviewForm(request.POST)

        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

            messages.success(
                request,
                'Ваш отзыв успешно добавлен.'
            )

            return redirect(product.get_absolute_url())

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
    }

    return render(
        request,
        'products/product_detail.html',
        context
    )


def product_search(request):
    query = request.GET.get('q', '').strip()

    products = Product.objects.filter(
        is_active=True,
        category__is_active=True
    ).select_related('category')

    if query:
        products = products.filter(
            name__icontains=query
        )
    else:
        products = Product.objects.none()

    context = {
        'query': query,
        'products': products,
    }

    return render(
        request,
        'products/search_results.html',
        context
    )


class ProductListAPIView(ListCreateAPIView):
    queryset = Product.objects.filter(
        is_active=True
    ).select_related('category')

    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

class ProductDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.filter(
        is_active=True
    ).select_related('category')

    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

class CategoryListAPIView(ListCreateAPIView):
    queryset = Category.objects.filter(
        is_active=True
    )

    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class CategoryDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.filter(
        is_active=True
    )

    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]