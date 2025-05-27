from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.\
    
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

