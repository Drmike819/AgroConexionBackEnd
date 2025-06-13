# Funcion que nos permite utilizar cuando se guarda un modelo en la base de datos
from django.db.models.signals import post_save
# Funcion que escucha cuando se guarda un modelo
from django.dispatch import receiver
# Funcion que nos permite acceder a la configuracion del proyecto
from django.conf import settings
# Importamos los modelos
from .models import ShoppingCart

from users.models import  CustomUser

# Cunado se crea un nuevo usuario
@receiver(post_save, sender=CustomUser)
# Ejecucion de la funcion
def create_user_cart(sender, instance, created, **kwargs):
    # Verifica si el usuario fue creado recientemente
    if created:
        # Creacion del carrito del usuario
        ShoppingCart.objects.create(user=instance)