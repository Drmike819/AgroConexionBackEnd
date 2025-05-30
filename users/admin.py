from django.contrib import admin
from .models import CustomUser, FavoriteProducts, ShoppingCart, CartProducts 
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Agregar los campos que quieres que se muestren en la vista de lista
    list_display = ('username', 'email', 'is_seller', 'is_buyer', 'first_name', 'last_name', 'phone_number')
    search_fields = ('username', 'email', 'phone_number')  # Campos que se pueden buscar
    list_filter = ('is_seller', 'is_buyer')  # Filtros

    # Agregar campos que quieres que se muestren al editar un usuario
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'address', 'phone_number', 'profile_image')
        }),
        ('Permissions', {
            'fields': ('is_seller', 'is_buyer')
        }),
    )
    # Para cambiar la vista de los campos cuando se crean o editan usuarios
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'address', 'phone_number', 'profile_image')
        }),
        ('Permissions', {
            'fields': ('is_seller', 'is_buyer')
        }),
    )

# Registra tu CustomUser con la configuración personalizada
admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(FavoriteProducts)

admin.site.register(ShoppingCart)

admin.site.register(CartProducts)