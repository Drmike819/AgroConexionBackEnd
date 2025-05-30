from rest_framework import serializers
from .models import CustomUser, FavoriteProducts
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from products.serializer import SerializerProducts

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
            raise ValidationError("Las contraseñas no coinciden.")
        
        # Validar la contraseña con las validaciones del sistema
        validate_password(password)
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


# Serializador para agregar un producto a favoritos
class FavoriteProductsSerializer(serializers.ModelSerializer):
    
    # llamamos al serializador de los productos, esto nos ayuda a tener la informaciond e los productos favoritos
    product = SerializerProducts(read_only=True)
    
    class Meta:
        # Modelo que utilizaremos
        model = FavoriteProducts
        # Campos que se incluirán en la serialización
        fields = ['id', 'user', 'product', 'added_at']
        # Indicamos que estos campos serán de solo lectura. 
        # El cliente no podrá modificarlos directamente.
        read_only_fields = ['id', 'user', 'added_at']

    # Función que valida que el usuario no agregue el mismo producto dos veces a favoritos
    def validate(self, attrs):
        # Obtenemos el usuario autenticado desde el contexto (enviado desde la vista)
        user = self.context['request'].user
        # Obtenemos el producto que el usuario desea agregar a favoritos
        product = attrs.get('product')

        # Validamos que el producto no haya sido ya agregado por este usuario
        if FavoriteProducts.objects.filter(user=user, product=product).exists():
            # Si ya existe, devolvemos un mensaje de error
            raise serializers.ValidationError("Este producto ya está en tus favoritos.")

        # Si todo está bien, devolvemos los datos validados
        return attrs
