from django.db import models
# Create your models here.

# creacion de la tabla favoritos
class FavoriteProducts(models.Model):
    # campo en donde indicamos la union entre usuario y la tabla favorito (si el usuario es eliminado la informacion se eliminara)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='favorites')
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
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE, related_name='shopping_cart')
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