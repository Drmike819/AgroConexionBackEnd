from rest_framework import serializers
from .models import CustomUser

# from rest_framework.response import Response
# from rest_framework import status
# from django.core.exceptions import ValidationError
# from django.contrib.auth import authenticate
# from django.contrib.auth.password_validation import validate_password

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

import re 
# Serializador de registro
class RegisterUserSerializer(serializers.ModelSerializer):
    # Definir la confirmación de contraseña como un campo adicional
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        # modelo que utilizaremos
        model = CustomUser
        # campos que se utilizaran 
        fields = ['username', 'email', 'password', 'password2']
        # indicamos que la contraseño solo se podra escribir
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    # funcion que valida el formulario
    def validate(self, data):
        """
        Verificar que las contraseñas coincidan.
        """
        # obtenemmos la informacion de los valores enviados y la guardamos en las variables
        password = data.get('password')
        password2 = data.get('password2')
        # verificamos si las contraseñas coinciden
        if password != password2:
            # mensaje deerror en caso de que estas no coincidan
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        
        if len(password) <= 8:
            raise serializers.ValidationError({"password": "La contraseña es muy corta"})
        
         # Debe tener al menos una mayúscula
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError({"password":"La contraseña debe contener al menos una letra mayúscula."})

        # Debe tener al menos una minúscula
        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError({"password":"La contraseña debe contener al menos una letra minúscula."})

        # Debe tener al menos un número
        if not re.search(r'\d', password):
            raise serializers.ValidationError({"password":"La contraseña debe contener al menos un número."})

        # Debe tener al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise serializers.ValidationError({"password":"La contraseña debe contener al menos un carácter especial."})

        
        # Validar la contraseña con las validaciones del sistema
        # validate_password(password)
        # retornados la informacion
        return data
    # funcion para crear un usuario
    def create(self, validated_data):
        """
        Crear el usuario con la contraseña hasheada.
        """
        # Eliminar la contraseña2 porque no es un campo real del modelo
        validated_data.pop('password2', None)
        
        # Crear el usuario
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        # retorna el usuario creado
        return user


# Serializador personalizado para manejar tokens de autenticación
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    # Este método verifica que el usuario inicie sesión con las credenciales correctas
    # attrs: parametros que el usuario envia a la hora de iniciar sesion
    def validate(self, attrs):
        # Llamamos al método original para validar y obtener los tokens
        data = super().validate(attrs)

        # Obtenemos el usuario que acaba de iniciar sesión
        user = self.user

        # Añadimos información adicional del usuario a la respuesta
        data.update({
            'userImage': user.profile_image.url,
            'userName': user.username,
            'userEmail': user.email,
            'isSeller': user.is_seller,
            'isBuyer': user.is_buyer,
        })

        # Retornamos los datos junto con los tokens y la información del usuario
        return data

