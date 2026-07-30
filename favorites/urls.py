from django.urls import path

from . import views


urlpatterns = [
    path('', views.favorite_list, name='favorite_list'),
    path('add/<int:product_id>/', views.favorite_add, name='favorite_add'),
    path('remove/<int:product_id>/', views.favorite_remove, name='favorite_remove'),
]