# Clase que nos permite configurar la aplicación
from django.apps import AppConfig

# Clase de configuración de la aplicación "users"
class UsersConfig(AppConfig):
    # Define el tipo de campo automático predeterminado para las claves primarias
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Indica el nombre de la aplicación
    name = 'users'
    
    # Función que se ejecuta al cargar la aplicación para registrar señales
    def ready(self):
        # Importamos el módulo de señales para que los receptores se activen
        from cart import signals

