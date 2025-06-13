from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from products.models import Products
from .serializer import RegisterUserSerializer, CustomTokenObtainPairSerializer
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


