from django.contrib import admin
from .models import Category, Products, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")  # Muestra ID y Nombre en la lista
    search_fields = ("name",)  # Agrega barra de búsqueda

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "producer", "state")  # Muestra estos campos en la lista
    search_fields = ("name", "producer__username")  # Permite buscar por nombre de producto o productor
    list_filter = ("state", "category")  # Agrega filtros laterales por estado y categoría
    autocomplete_fields = ("producer",)  # Permite buscar el productor en un cuadro de autocompletado
    filter_horizontal = ("category",)  # Muestra categorías como un selector múltiple

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image")