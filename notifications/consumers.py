# Nos permite utilizar funciones asincronicas
from channels.generic.websocket import AsyncWebsocketConsumer
import json

# Consumer(View en django)  hereada para utilizar funcion asincronicas
class NotificationConsumer(AsyncWebsocketConsumer):
    # Fucion de conexion
    async def connect(self):
        # obtenemos el usuario mediante el scope(request)
        user = self.scope["user"]
        # Si no se puede obtener el usuario
        if user.is_anonymous:
            # Cerramos la conexion
            await self.close()
        else:
            # Creamos el grupo del usuario
            self.group_name = f"user_{user.id}"
            # Agregamos el usuario logeado a su canal 
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            # Aceptamos la conexion 
            await self.accept()

    # Funcion para desconectar el usuario del grupo
    async def disconnect(self, close_code):
        # Cunado el usuario cierra sesion o se deconecta del grupo
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Funcuion que envia los datos de la notificacion
    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["content"]))


