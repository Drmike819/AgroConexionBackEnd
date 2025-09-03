from .models import Notification
from rest_framework import serializers

# Serializador para obtener las notificaciones
class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'