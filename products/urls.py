from django.urls import path

from . import views


urlpatterns = [
    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'category/<slug:slug>/',
        views.category_detail,
        name='category_detail'
    ),

    path(
        'product/<slug:slug>/',
        views.product_detail,
        name='product_detail'
    ),

    path(
        'search/',
        views.product_search,
        name='product_search'
    ),

    path(
        'api/products/',
        views.ProductListAPIView.as_view(),
        name='api_products'
    ),

    path(
        'api/products/<int:pk>/',
        views.ProductDetailAPIView.as_view(),
        name='api_product_detail'
    ),

    path(
        'api/categories/',
        views.CategoryListAPIView.as_view(),
        name='api_categories'
    ),

    path(
        'api/categories/<int:pk>/',
        views.CategoryDetailAPIView.as_view(),
        name='api_category_detail'
    ),
]