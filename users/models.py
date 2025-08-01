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
    profile_image = models.ImageField(upload_to="profile_pictures/", blank=True, null=True, default='media/profile_pictures/perfil.jpeg')
    
    USER_TYPE_CHOICES = [
        ('common', 'Usuario común'),
        ('group', 'Agrupación campesina'),
        ('admin', 'Administrador'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='common')
    
    # Tipo de usuario: comprador o vendedor
    is_seller = models.BooleanField(default=False)
    # Celular del usuario
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    
    

    def save(self, *args, **kwargs):
        # Aseguramos que solo uno de los dos campos (comprador o vendedor) pueda ser verdadero
        if self.user_type == 'group':
            self.is_seller = True
        super().save(*args, **kwargs)
        
    # Sobrescribimos el método __str__ para que sea más legible
    def __str__(self):
        return self.username
    
    
# Modelo para garegar informacion si el usuario es una agrupacion 
class GroupProfile(models.Model):
    # Usuario asociado 
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='group_profile')
    # NIT de la agrupacion
    nit = models.CharField(max_length=20, blank=True, null=True)
    # Tipo de agrupacion
    organization_type = models.CharField(max_length=100, choices=[
        ('cooperative', 'Cooperativa'),
        ('association', 'Asociación'),
        ('informal', 'Grupo informal'),
        ('other', 'Otro'),
    ], default='other')
    # Nombre del representante legal
    legal_representative = models.CharField(max_length=150)
    # Cedula
    representative_cedula = models.CharField(max_length=20)
    # Imagen de la cedula
    image_cedula = models.ImageField(upload_to="documents/cedula/", blank=True, null=True,)
    # Rut
    rut_document = models.FileField(upload_to='documents/rut/', null=True, blank=True)

    def __str__(self):
        return f"(Agrupación {self.user.username})"

