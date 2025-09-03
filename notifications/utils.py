from .models import Notification
from channels.layers import get_channel_layer
# Nos permite utlizar funciona asincronicas
from asgiref.sync import async_to_sync

def send_notification(user, type, title, message, image=None, data=None):
    # Guardar en base de datos
    notification = Notification.objects.create(
        user=user,
        type=type,
        title=title,
        message=message,
        image=image,
        data=data or {}
    )
    
    # Obtenemos la informacion de la notificacion
    data = {
        "id": notification.id,
        "type": notification.type,
        "title": notification.title,
        "message": notification.message,
        "image": notification.image if notification.image else None,
        "data": notification.data,
        "created_at": notification.created_at.isoformat(),
    }

    # Enviar por WebSocket
    # Obtenemos la configracion para utilizar la conexion asincronica de redis
    channel_layer = get_channel_layer()
    # Llammao a channel_layer
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "content": {
                "id": notification.id,
                "title": title,
                "message": message,
                "image": image,
                "type": type,
                "data": data,
                "created_at": str(notification.created_at),
                "read": notification.is_read,
            }
        }
    )
    
    # Retornamos la informacion para que el front lo consumos
    return data

