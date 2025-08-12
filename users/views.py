from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .serializer import RegisterUserSerializer, RegisterGroupSerializer, UserUpdateSerializer, ConfirmPasswordChangeSerializer
from .models import EmailVerificationToken, CustomUser
from .utils.email_service import EmailService
# Create your views here.

#  Vista que nos permite obtener la informacion del usuario logeado
class CurrentUserView(APIView):
    # Tipo de autentificacion solicitada
    authentication_classes = [JWTAuthentication]
    # Permiso de la VIEW
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserUpdateSerializer(request.user)
        return Response(serializer.data)
    
    
# Vista para el registro de usuarios   
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    # si el metodo de peticion es (POST)
    def post(self, request, *args, **kwargs):
        serializer = RegisterUserSerializer(data = request.data)
        # envia los datos del cliente
        if serializer.is_valid():
            # Creamos la agrupacion
            user = serializer.save()
            # Enviamos mensaje de exito
            return Response({
                "message": "Te haz registrado correctamente",
                "username": user.username,
                "email": user.email,
            }, status=status.HTTP_201_CREATED)
        # Si no es valido enviamos mensaje de error
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


# Vista para verificar la cuenta
class VerifyAccountView(APIView):
    # Tipo d permido que exige la VIEW
    permission_classes = [AllowAny]

    # Method POST
    def post(self, request):
        # Obtenemos el email del usuario
        email = request.data.get("email")
        # Obtenemos el codigo de verificacion
        code = request.data.get("code")

        try:
            # Verificamos que el usuario exista
            user = CustomUser.objects.get(email=email)
            # Verificamos que el codigo exista
            token_obj = EmailVerificationToken.objects.filter(
                user=user, purpose='account_verification', code=code
            ).last()

            # Verificamos que el codigo exista y que no eet expirado
            if not token_obj or token_obj.is_expired():
                return Response({"error": "Código inválido o expirado."}, status=400)

            # Activamos la cuenta del usuario
            user.is_active = True
            user.save()
            # Eliminamos el codigo de verificacion
            token_obj.delete()
            # Mensaje de exito
            return Response({"message": "Cuenta verificada con éxito."}, status=200)
        # Mensaje de error
        except CustomUser.DoesNotExist:
            return Response({"error": "Usuario no encontrado."}, status=404)


# Vista que permite elegir al usuario la verificacion en dos pasos
class ToggleTwoFactorView(APIView):
    # Tipo de autentificacion solicitada
    authentication_classes = [JWTAuthentication]
    # Permiso de la VIEW
    permission_classes = [IsAuthenticated]

    # Method POST
    def post(self, request):
        # Obtenemos si el usuario quiere activar o no, si no ponemos obtenerlo sera none
        enable_2fa = request.data.get("enable", None)

        # Mensaje de error a la hora de activar o desactivar
        if enable_2fa is None:
            return Response({"error": "Debe indicar si quiere activar o desactivar el 2FA."}, status=400)

        # Activa o desactiva la autenticacion
        request.user.two_factor_enabled = bool(enable_2fa)
        # Guarda los cambios
        request.user.save()

        # Mensaje indentificando el estado
        status_str = "activada" if request.user.two_factor_enabled else "desactivada"
        # Mensaje de exito
        return Response({"message": f"Autenticación en dos pasos {status_str} correctamente."})


# Vista que permite que el usuario inicie sesion, incluyendo 2FA
class LoginView(APIView):
    # Permisos que solicita la view
    permission_classes = [AllowAny]

    # Method POST
    def post(self, request):
        # Obtenemos la informacion del usuario
        username = request.data.get("username")
        password = request.data.get("password")

        try:
            # Obtenemos el usuario 
            user = CustomUser.objects.get(username=username)
            # Verificamos la contraseña            
            if not user.check_password(password):
                return Response({"error": "Credenciales inválidas"}, status=400)
            # Verificamso que la cuenta este verificada
            if not user.is_active:
                return Response({"error": "Cuenta no verificada"}, status=403)

            # Si no tiene la 2FA inicia sesion de manera normal
            if not user.two_factor_enabled:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "userImage": user.profile_image.url if user.profile_image else None,
                    "userName": user.username,
                    "userEmail": user.email,
                    "isSeller": user.is_seller
                })

            # Si tiene 2FA activo envia codigo de verificacion
            token_obj = EmailVerificationToken.create_token(user, 'two_factor', use_code=True)
            EmailService.send_email(
                "Código de verificación de acceso",
                f"Tu código es: {token_obj.code}",
                [user.email]
            )
            return Response({"message": "Código enviado a tu correo."}, status=200)
        # Mensaje de error si el usuario no existe
        except CustomUser.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)


# Vista para iniciar sesion en dos pasos
class LoginViewStep2(APIView):
    # Permisos de la VIEW
    permission_classes = [AllowAny]

    # Method POST
    def post(self, request):
        # Obtenemos la informacion del usuario       
        email = request.data.get("email")
        code = request.data.get("code")

        try:
            # Obtenemos al usuario
            user = CustomUser.objects.get(email=email)
            # Obtenemos el token de validacion
            token_obj = EmailVerificationToken.objects.filter(
                user=user, purpose='two_factor', code=code
            ).last()
            # Verificamos que exista y no este expirado
            if not token_obj or token_obj.is_expired():
                return Response({"error": "Código inválido o expirado"}, status=400)

            # Generar JWT
            refresh = RefreshToken.for_user(user)
            # Eliminamos el token 
            token_obj.delete()

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "userImage": user.profile_image.url if user.profile_image else None,
                "userName": user.username,
                "userEmail": user.email,
                "isSeller": user.is_seller
            })
        # Mensaje de error
        except CustomUser.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)
        

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
    
    
# Vista para actualizar la contraseña del usuario(codigo de verificacion)
class RequestPasswordChangeView(APIView):
    # Metodo de autenticacion
    authentication_classes = [JWTAuthentication]
    # Permiso solicitado de la VIEW
    permission_classes = [IsAuthenticated]

    # Method POST
    def post(self, request):
        # Creamos el token de validacion
        token_obj = EmailVerificationToken.create_token(
            request.user, 'password_change', use_code=True
        )
        # Creamos y enviamos el correo con el codigo de verificacion
        EmailService.send_email(
            "Confirma el cambio de contraseña",
            f"Tu código es: {token_obj.code}",
            [request.user.email]
        )
        return Response({"message": "Código enviado a tu correo."})


# Vista que permite actualizar la contraseña
class ConfirmPasswordChangeView(APIView):
    # Metodo de autenticacion
    authentication_classes = [JWTAuthentication]
    # Permiso solicitado de la VIEW
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Obtenenmos el serializador parta cambiar la contraseña
        serializer = ConfirmPasswordChangeSerializer(data=request.data)
        # Verificamos que sea valido
        serializer.is_valid(raise_exception=True)
        # Obtenemos el codigo
        code = serializer.validated_data['code']
        # L anueva contraseña
        new_password = serializer.validated_data['new_password']
        # Verificamos que el codigo de verificacion exista
        token_obj = EmailVerificationToken.objects.filter(
            user=request.user, purpose='password_change', code=code
        ).last()

        # Verificamos que exista o que no este expirado
        if not token_obj or token_obj.is_expired():
            return Response({"error": "Código inválido o expirado"}, status=400)
        # Cambiamos la contraseña del usuario 
        request.user.set_password(new_password)
        # Guardamos los cambios
        request.user.save()
        # Eliminamos el codigo
        token_obj.delete()
        # Mensaje de exito
        return Response({"message": "Contraseña cambiada con éxito."})


# Visdta que nos envia el codigo de verificacion para cambiar la contraseña
class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]

    # Method POST
    def post(self, request):
        # Obtenemos el email de la peticion
        email = request.data.get("email")
        
        try:
            # Verificamos el usuario
            user = CustomUser.objects.get(email=email)

            # Crear token con código
            token_obj = EmailVerificationToken.create_token(
                user, 'password_reset', use_code=True
            )

            # Enviar email 
            EmailService.send_email(
                "Codigo de verificacion cambio de contraseña",
                f"Tu codigo es: {token_obj.code}",
                [user.email]
            )
            # Respuesta de exito
            return Response({"message": "Código de recuperación enviado a tu correo."})
        # Respuesta de error en caso de que el correo no sea el correcto
        except CustomUser.DoesNotExist:
            return Response({"error": "No existe una cuenta con ese correo."}, status=404)


# Vista que nos cambia la contraseña
class ConfirmPasswordResetView(APIView):
    permission_classes = [AllowAny]

    # Method POST
    def post(self, request):
        # Obtenemos al informacion de la peticion
        email = request.data.get("email")
        code = request.data.get("code")
        new_password = request.data.get("new_password")

        # Obtenemos el serializador 
        serializer = ConfirmPasswordChangeSerializer(data=request.data)
        # Lo validamos
        serializer.is_valid(raise_exception=True)

        try:
            # Obtenemos el usuario
            user = CustomUser.objects.get(email=email)
            # Creamos el codigo
            token_obj = EmailVerificationToken.objects.filter(
                user=user, purpose='password_reset', code=code
            ).last()

            # Verificamos que exista y que no este expirado 
            if not token_obj or token_obj.is_expired():
                return Response({"error": "Código inválido o expirado"}, status=400)

            # Cambiar contraseña
            user.set_password(new_password)
            user.save()

            # Eliminar token
            token_obj.delete()
            # Mensaje de xito
            return Response({"message": "Contraseña restablecida correctamente."})
        # Mensaje de error en caso de no encontrar el usuario
        except CustomUser.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)
