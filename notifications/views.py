from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .serializer import (
    NotificationsSerializer
)
from rest_framework.views import APIView
from .models import Notification
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
# Create your views here.

# View que nos permite obtener las notificaciones del usuariuo logeado
class NotificatiosnView(APIView):
    # Solo los usuarios con token JWT pueden acceder
    authentication_classes = [JWTAuthentication]
    # Solo usuarios autenticados pueden acceder
    permission_classes = [IsAuthenticated]
    
    # METHOD GET
    def get(self, request, *args, **kwargs):
        # Obtenemos el usuario que envia la peticion
        user = request.user
        # Obtenemos la notificaciones del usuario
        notifications = Notification.objects.filter(user=user).order_by('created_at')
        
        # Verificamos si el usuario tiene productos
        if not notifications.exists():
            return Response(
                {'message': 'Notienes notificaciones'}, 
                status=status.HTTP_200_OK
            )
        # Obtenemos el serializador y le pasamos los datos
        serializer = NotificationsSerializer(notifications, many=True)
        # Retornamos la informacion
        return Response(serializer.data, status=status.HTTP_200_OK)
        

# View para eliminar uina notificacion
class DeleteNotificationView(APIView):
    
    # Funcion para obtener la notificacion
    def get_object(self, request, notification_id):
        # Obtenemos el usuario de la peticion
        user = request.user
        # Obtenemos el comentario y lo retornamos 
        try:
            return Notification.objects.get(id=notification_id, user=user)
        except  Notification.DoesNotExist:
            # En caso de no obtenerlo enviamos none
            return None
        
    # Method DELETE
    def delete(self, request, notification_id, *args, **kwargs):
        # Obtenemos la notificacion
        notification = self.get_object(request, notification_id)
        # Si no hay notificacion retornamos mensaje de error
        if not notification:
            return Response({'notification': 'La notificacion no fue encontrada o no tienes permisos para eliminarla'},status=status.HTTP_404_NOT_FOUND) 
        
        # Eliminamos la notificacion
        notification.delete()
        
        # Retornamos mensaje de exito
        return Response(
            {'message': f'Notificacion eliminada correctamente'}, 
            status=status.HTTP_200_OK
        )