from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .serializer import RegisterUserSerializer, CustomTokenObtainPairSerializer, RegisterGroupSerializer, UserUpdateSerializer
# Create your views here.

# Vista para el registro de usuarios
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    # otarga permisos a los usuarios si estan o no autentificados
    serializer_class = RegisterUserSerializer

    # si el metodo de peticion del cliente es (GET)
    def get(self, request, *args, **kwargs):
        # informacion que otorgara la api
        fields = [
            {"name": "username", "label": "Nombre de usuario", "type": "text", "required": True},
            {"name": "email", "label": "Email", "type": "email", "required": True},
            {"name": "password", "label": "Contraseña", "type": "password", "required": True},
            {"name": "password2", "label": "Confirmar Contraseña", "type": "password", "required": True},
        ]
        # retornara un diccionario
        return Response({"fields": fields})
    # si el metodo de peticion es (POST)
    def post(self, request, *args, **kwargs):
        # envia los datos del cliente
        return super().post(request, *args, **kwargs)


# Vista  que nos permite registrar una agrupacion
class RegisterGroupView(APIView):
    # Indcamos el permiso que pide la vista
    permission_classes = [AllowAny]

    # Metodo post para crear al usuario
    def post(self, request, *args, **kwargs):
        # Indicamos el serializador a utilizar
        serializer = RegisterGroupSerializer(data=request.data)

        # Verificamos que el serializador se avalido
        if serializer.is_valid():
            # Creamos la agrupacion
            user = serializer.save()
            # Enviamos mensaje de exito
            return Response({
                "message": "Agrupación registrada exitosamente.",
                "username": user.username,
                "email": user.email,
                "user_type": user.user_type,
            }, status=status.HTTP_201_CREATED)
        # Si no es valido enviamos mensaje de error
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# vista para el manejo del login del usuario, este por su clase heredada ya maneja el tema de los TOKENS
class LoginView(TokenObtainPairView):
    # indicamos el permiso que requiera la VIEW en este caso no necesita autenticacion
    permission_classes = [AllowAny]
    
    # inidcamos que utilizaremos nuestro serialiador persoanlizado, este nos retorna la informacion del usuario
    serializer_class = CustomTokenObtainPairSerializer
    
    # el metodo get nos devuelve los campos del formulario que requerimos para iniciar sesion
    def get(self, request, *args, **kwargs):
        fields = [
            {"name": "username", "label": "Nombre de usuario", "type": "text", "required": True},
            {"name": "password", "label": "Contraseña", "type": "password", "required": True},
        ]
        # retornamos los campos
        return Response({"fields": fields})


# Vista para cerrar sesion
class LogoutView(APIView):
    # Permisos de autentificacion y de acceso a la vista
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # Metodo post
    def post(self, request):
        # Obtenemos el refresh token del usuario
        refresh_token = request.data.get("refresh")

        # Si no lo encontramos
        if not refresh_token:
            return Response({"detail": "Refresh token requerido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # En caso de obtener el token lo enviaomos a la lista negra
            token = RefreshToken(refresh_token)
            token.blacklist()
            # Enviamos mensaje de exito
            return Response({"detail": "Sesión cerrada exitosamente."}, status=status.HTTP_200_OK)
        except TokenError:
            # Mensaje de error
            return Response({"detail": "Token inválido o ya expirado."}, status=status.HTTP_400_BAD_REQUEST)


# Vista que em permite actualizar la informacion del usuario
class UserUpdateView(APIView):
    # Permisos de autentificacion y de acceso a la vista
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def put(sel, request):
        # Obtenemos al usuario que envio la peticion
        user =  request.user
        # Obtenemos el serializador enviando a le usuario, la informacion a actualizar y indicamos que no requerimos todos los campos
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        
        # Verificamos que el serializador sea valido 
        if serializer.is_valid():
            # Y guardamos la informacion
            serializer.save()
            # Mensjae de exito
            return Response({
                "message": "Usuario actualizado correctamente",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        # Mensaje de error
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    