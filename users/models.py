from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.\


# creacion del modelo de usuario customizado 
class CustomUser(AbstractUser):
    # Email debe ser único
    email = models.EmailField(max_length=100, unique=True, null=False, blank=False)
    # Dirección del usuario
    address = models.TextField(max_length=500, null=True, blank=True)
    # Imagen de perfil
    profile_image = models.ImageField(upload_to="profile_pictures/", blank=True, null=True, default='profile_pictures/perfil.jpeg')
    # Tipo de usuario: comprador o vendedor
    is_seller = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=True)
    # Celular del usuario
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    
    # Sobrescribimos el método __str__ para que sea más legible
    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Aseguramos que solo uno de los dos campos (comprador o vendedor) pueda ser verdadero
        if self.is_seller:
            self.is_buyer = False
        else:
            self.is_buyer = True
        
        super().save(*args, **kwargs)


# creacion de la tabla favoritos
class FavoriteProducts(models.Model):
    # campo en donde indicamos la union entre usuario y la tabla favorito (si el usuario es eliminado la informacion se eliminara)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    # campo en donde indicamos la union entre producto y la tabla favoritos (si el producto es eliminado la informacion se eliminara)
    product = models.ForeignKey('products.Products', on_delete=models.CASCADE, related_name='favorited_by')
    # campo de la fecha de agregacion a favoritos
    added_at = models.DateTimeField(auto_now_add=True)

    # clase que nos permite indicar que un usuario no puede repetir un producto en favoritos
    class Meta:
        unique_together = ('user', 'product')
    
    # Mensaje que se mostrara en el admina
    def __str__(self):
        return f"Favoritos de {self.user.username}"
        
        
# Creación de la tabla Carrito de Compras
class ShoppingCart(models.Model):
    # Relación uno a uno: cada usuario tendrá un único carrito, y un carrito pertenece a un solo usuario
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='shopping_cart')
    # Fecha de creación del carrito
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Representación en el panel de administración de Django
    def __str__(self):
        return f"Carrito de {self.user.username}"


# Creación de la tabla Productos del Carrito
class CartProducts(models.Model):
    # Relación muchos a uno con el carrito: un carrito puede tener varios productos
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='products')
    # Relación muchos a uno con el producto: un producto puede estar en muchos carritos
    product = models.ForeignKey('products.Products', on_delete=models.CASCADE)
    # Cantidad del producto que el usuario desea comprar
    quantity = models.PositiveIntegerField(default=1)

    # Restricción para evitar productos duplicados en el mismo carrito
    class Meta:
        unique_together = ('cart', 'product')

    # Representación en el panel de administración de Django
    def __str__(self):
        return f"{self.quantity} x {self.product.name} en el carrito de {self.cart.user.username}"
