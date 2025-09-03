from django.db import models
from users.models import CustomUser
# Create your models here.

# Modelo de notificacion
class Notification(models.Model):
    # Indicamos los posibles tipos de notificacion
    NOTIFICATION_TYPES = [
        ('purchase', 'Compra'),
        ('new_category', 'Nueva Categoría'),
        ('custom', 'Personalizada'),
    ]
    # Uusrio al que se le asocia la notificacion
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # Tipo de notificacion
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    # Cuerpo de la notificacion
    title = models.CharField(max_length=255)
    message = models.TextField()
    image = models.URLField(blank=True, null=True)
    data = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # Mensaje que vemos en el admin
    def __str__(self):
        return f'Notificacion para el {self.user.username}'