from django.contrib import admin

from .models import FavoriteProducts, ShoppingCart, CartProducts
# Register your models here.

admin.site.register(ShoppingCart)
admin.site.register(FavoriteProducts)
admin.site.register(CartProducts)