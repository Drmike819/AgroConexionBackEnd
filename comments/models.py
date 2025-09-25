from django.db import models

from users.models import CustomUser
from products.models import Products
from campeche_backend.storages import PublicMediaStorage

# Create your models here.

# Modelo de comentarios
class Comments(models.Model):
    # Coneccion con el usuario
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="comment_user")
    # Coneccion con el producto a comentar
    product = models.ForeignKey(Products, on_delete=models.Case, related_name='comment')
    # Campo de texto en donde se alamcenara el comentarioo
    comment = models.TextField(null=False, blank=False)
    
    
    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
    
    # Funcion que retorna un mensaje
    def __str__(self):
        return f"el usuario {self.user.username} comento el producto {self.product.name} del productor {self.product.producer}"
    

# Modelo para incluir imagenes a los comentario
class CommentsImage(models.Model):
    # Conexion con el comentario
    comment = models.ForeignKey(Comments, on_delete=models.CASCADE, related_name="images")
    # Campo en donde se alamcenara la imagen
    image = models.ImageField(upload_to="comments_pictures/", null=True, blank=True, storage=PublicMediaStorage())
    
    class Meta:
        verbose_name = "Image Comment"
        verbose_name_plural = "Images Comments"

    # Funcion que retorna un mensaje
    def __str__(self):
        return f"Imagen del comentario {self.comment.comment}"