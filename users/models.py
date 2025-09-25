from django.contrib.auth.models import AbstractUser
from django.db import models
from campeche_backend.storages import PublicMediaStorage
# Modulo para crear identificadores unicos 
import uuid
# Manejo de horarios y tiempos dependiendo de la zona horaria
from django.utils import timezone
# permite sumar o restar intervalos de tiempo a objetos de fecha y hora.
from datetime import timedelta
# Create your models here.\


# creacion del modelo de usuario customizado 
class CustomUser(AbstractUser):
    # Email debe ser único
    email = models.EmailField(max_length=100, unique=True, null=False, blank=False)
    # Dirección del usuario
    address = models.TextField(max_length=500, null=True, blank=True)
    # Imagen de perfil
    profile_image = models.ImageField(upload_to="profile_pictures/",storage=PublicMediaStorage(), blank=True, null=True, default='/profile_pictures/perfil.jpeg')
    
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
    
    two_factor_enabled = models.BooleanField(default=False)
    

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
    image_cedula = models.ImageField(upload_to="documents/cedula/",storage=PublicMediaStorage(), blank=True, null=True,)
    # Rut
    rut_document = models.FileField(upload_to='documents/rut/',storage=PublicMediaStorage(), null=True, blank=True)

    def __str__(self):
        return f"(Agrupación {self.user.username})"


# Modelo de creacionde los tokens o de codigo
class EmailVerificationToken(models.Model):
    # Lista de obpciones para idicar para que se utilizara el token
    PURPOSE_CHOICES = [
        ('account_verification', 'Account Verification'),
        ('two_factor', 'Two Factor Auth'),
        ('password_change', 'Password Change'),
        ('password_reset', 'Password Reset'),
    ]
    # Indicamos la union de los tokens al usuario
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    # Campo de generacion de tpken, este no se podra repetir y tampoco modificar
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # Codigo para verificar en dos pasos
    code = models.CharField(max_length=6, null=True, blank=True)  # PIN numérico opcional
    # Indicaodr de utilidad del token
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES)
    # Fecha y horta de creacion
    created_at = models.DateTimeField(auto_now_add=True)
    # Fecha y hora de expiracion del token
    expires_at = models.DateTimeField()

    # Verificacion de expiracion del token
    def is_expired(self):
        return timezone.now() > self.expires_at

    # Metodo para crear el token del usuario
    @classmethod
    def create_token(cls, user, purpose, use_code=False, expire_minutes=15):
        token_obj = cls(
            user=user,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=expire_minutes)
        )
        if use_code:
            import random
            token_obj.code = f"{random.randint(100000, 999999)}"
        token_obj.save()
        return token_obj