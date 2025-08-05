from rest_framework import serializers
from .models import CustomUser, GroupProfile, EmailVerificationToken
from .utils.email_service import EmailService
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
            password=validated_data['password'],
            is_active=False
        )
        
        # Crea mensaje y token para verificar la cuenta
        token_obj = EmailVerificationToken.create_token(user, 'account_verification', use_code=True)
        EmailService.send_email(
            "Confirma tu cuenta",
            f"Tu código de verificación es: {token_obj.code}\n\n"
            "Ingresa este código en la página de verificación para activar tu cuenta.",
            [user.email]
        )
        
        # retorna el usuario creado
        return user


# Serializer para obtener los campos de modelo de agrupacion
class GroupProfileSerializer(serializers.ModelSerializer):
    class Meta:
        # Obtenemos el modelo a autilizar
        model = GroupProfile
        # Indicamos los campos que solicitaremos
        fields = [
            'nit',
            'organization_type',
            'legal_representative',
            'representative_cedula',
            'image_cedula',
            'rut_document',
        ]
        

# Serializer para registrar a un agrupacion
class RegisterGroupSerializer(serializers.ModelSerializer):
    # Creamos un campode contraseña para validarla
    password2 = serializers.CharField(write_only=True, required=True)
    # Obtenemos los campos del serializer de las agrupaciones
    group_profile = GroupProfileSerializer()

    # Indicamos el modelo que utilizaremos
    class Meta:
        model = CustomUser
        # Campos a utilizar
        fields = [
            'username',
            'email',
            'password',
            'password2',
            'phone_number',
            'address',
            'profile_image',
            'group_profile',
        ]
        # Indicamso que la contraseña solo sera de lectura
        extra_kwargs = {
            'password': {'write_only': True},
        }

    # Validaciones de contraseña
    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        if len(password) <= 8:
            raise serializers.ValidationError({"password": "La contraseña es muy corta"})
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError({"password": "Debe contener al menos una mayúscula."})
        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError({"password": "Debe contener al menos una minúscula."})
        if not re.search(r'\d', password):
            raise serializers.ValidationError({"password": "Debe contener al menos un número."})
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise serializers.ValidationError({"password": "Debe contener un carácter especial."})
        # Obtenemos la informacion de las contraseñas
        return data

    # Creacion de la agrupacion
    def create(self, validated_data):
        # Obtenemos la informacion de la agrupacion
        group_data = validated_data.pop('group_profile')
        # Eliminamos la contraseña 2
        validated_data.pop('password2')

        # creamso al usuario en este caso en la agrupacion
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number'),
            address=validated_data.get('address'),
            profile_image=validated_data.get('profile_image'),
            user_type='group',  # Forzar que sea agrupación
            is_active=False
        )

        # Creamos la informacion adicional de la agrupacion
        GroupProfile.objects.create(user=user, **group_data)
        
        # Creamos mensaje y token para confirmar la cuenta
        token_obj = EmailVerificationToken.create_token(user, 'account_verification', use_code=True)
        EmailService.send_email(
            "Confirma tu cuenta",
            f"Tu código de verificación es: {token_obj.code}\n\n"
            "Ingresa este código en la página de verificación para activar tu cuenta.",
            [user.email]
        )
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
        })

        # Retornamos los datos junto con los tokens y la información del usuario
        return data


# Serializer para actualizar los datos del usuario
class UserUpdateSerializer(serializers.ModelSerializer):
    # Obtenemos el serializador de las Grupaciones y le indicamos que no es requerido
    group_profile = GroupProfileSerializer(required=False)
    
    class Meta:
        # Indicamos el modelo a utilizar
        model = CustomUser
        # Campos que solicitaremos
        fields = [
            'username',
            'email',
            'phone_number',
            'address',
            'profile_image',
            'is_seller',
            'group_profile',
        ]
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
        } 
    
    # Funcion que permite actualizar a el usuario
    def update(self, instance, validated_data):
        # Verificamos si el usuario es una agrupacion y obtenemos al informacion en caso de que no lo sea se retorna un none
        group_data = validated_data.pop('group_profile', None)
        
        # Recorremos cada campo y le asignamos el valor 
        for attr, value in validated_data.items():
            # Asignamos los valores a la instancia
            setattr(instance, attr, value)
        # Guardamos la instancia
        instance.save()
        
        # Verificamos si el group_data existe y lo agregamos a la instancia
        if group_data and hasattr(instance, 'group_profile'):
            group_instance = instance.group_profile
            # Recorremso los valores de group_data y asiganamos su informacion
            for attr, value in group_data.items():
                setattr(instance, attr, value)
            # Guardamos la instancia
            group_instance.save()
        
        # Retornamos el el objeto actualizado
        return instance
    
    
# Serializador para cambiar la contraseña
class ConfirmPasswordChangeSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        # Coincidencia
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password": "Las contraseñas no coinciden."})

        # Longitud mínima
        if len(data['new_password']) <= 8:
            raise serializers.ValidationError({"new_password": "La contraseña es muy corta."})

        # Mayúscula
        if not re.search(r'[A-Z]', data['new_password']):
            raise serializers.ValidationError({"new_password": "Debe contener al menos una letra mayúscula."})

        # Minúscula
        if not re.search(r'[a-z]', data['new_password']):
            raise serializers.ValidationError({"new_password": "Debe contener al menos una letra minúscula."})

        # Número
        if not re.search(r'\d', data['new_password']):
            raise serializers.ValidationError({"new_password": "Debe contener al menos un número."})

        # Carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', data['new_password']):
            raise serializers.ValidationError({"new_password": "Debe contener al menos un carácter especial."})

        return data