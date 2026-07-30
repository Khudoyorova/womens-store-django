from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product
from .models import Favorite


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(
        user=request.user
    ).select_related('product', 'product__category')

    return render(
        request,
        'favorites/favorite_list.html',
        {'favorites': favorites}
    )


@login_required
def favorite_add(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect('favorite_list')


@login_required
def favorite_remove(request, product_id):
    favorite = get_object_or_404(
        Favorite,
        user=request.user,
        product_id=product_id
    )

    favorite.delete()

    return redirect('favorite_list')