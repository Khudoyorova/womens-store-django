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
]