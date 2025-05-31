from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import FavoriteProducts, ShoppingCart, CartProducts
from products.models import Products
from .serializer import RegisterUserSerializer, CustomTokenObtainPairSerializer, FavoriteProductsSerializer, CartProductsUserSerializer, CartUserSerializer
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


# Vista que nos permite ver y agregar productos a favoritos
class FavoritesView(APIView):
    # Indicamos el método de autenticación
    authentication_classes = [JWTAuthentication]
    # Solo los usuarios autenticados pueden acceder a esta vista
    permission_classes = [IsAuthenticated]
    
    # Método GET: obtiene los productos favoritos del usuario autenticado
    def get(self, request, *args, **kwargs):
        # Filtramos los productos favoritos por el usuario autenticado
        favorite = FavoriteProducts.objects.filter(user=request.user)
        # Serializamos los productos favoritos
        serializer = FavoriteProductsSerializer(favorite, many=True)
        # Retornamos la lista de productos favoritos
        return Response(serializer.data)
    
    # Método POST: permite agregar un nuevo producto a favoritos
    def post(self, request, *args, **kwargs):
        serializer = FavoriteProductsSerializer(
            # Enviamos los datos enviados por el cliente (product_id)
            data=request.data,
            # Enviamos también el request completo como contexto para acceder a request.user en el serializador
            context={'request': request}
        )
        # Validamos el serializador
        if serializer.is_valid():
            # Si es válido, guardamos el objeto asignando automáticamente el usuario autenticado
            serializer.save(user=request.user)
            # Retornamos la información del producto favorito creado
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # Si los datos no son válidos, retornamos los errores
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
# Vista que nos permite eliminar un producto de la lista de favoritos
class FavoriteDeleteView(APIView):
    # Indicamos el método de autenticación
    authentication_classes = [JWTAuthentication]
    # Solo los usuarios autenticados pueden acceder a esta vista
    permission_classes = [IsAuthenticated]

    # Método DELETE: permite eliminar un producto específico de los favoritos del usuario
    def delete(self, request, product_id, *args, **kwargs):
        try:
            # Buscamos el producto favorito por el usuario autenticado y el ID del producto recibido
            favorite = FavoriteProducts.objects.get(
                user=request.user,
                product_id=product_id
            )
            # Eliminamos el registro encontrado
            favorite.delete()
            # Retornamos una respuesta de éxito sin contenido
            return Response(
                {"detail": "Producto eliminado de favoritos correctamente."},
                status=status.HTTP_204_NO_CONTENT
            )
        # Si no se encuentra el producto favorito, retornamos un error 404
        except FavoriteProducts.DoesNotExist:
            return Response(
                {"detail": "El producto no está en tus favoritos."},
                status=status.HTTP_404_NOT_FOUND
            )


# Vista que nos permite obtener y agregar los productos del carrito
class CartUserView(APIView):
    # Indicamos el método de autenticación
    authentication_classes = [JWTAuthentication]
    # Solo los usuarios autenticados pueden acceder a esta vista
    permission_classes = [IsAuthenticated]

    # GET: Obtiene todos los productos del carrito del usuario autenticado
    def get(self, request, *args, **kwargs):
        try:
            # Obtenemos el carrito del usuario autenticado
            cart = ShoppingCart.objects.get(user=request.user)
        except ShoppingCart.DoesNotExist:
            # Si el usuario no tiene un carrito, se devuelve un mensaje de error
            return Response({"detail": "El usuario no tiene un carrito."}, status=status.HTTP_404_NOT_FOUND)

        # Serializamos y devolvemos la información del carrito
        serializer = CartUserSerializer(cart)
        return Response(serializer.data)

    # POST: Agrega un producto al carrito del usuario autenticado
    def post(self, request, *args, **kwargs):
        # Obtenemos el ID del producto del cuerpo de la solicitud
        product_id = request.data.get('product_id')
        # Obtenemos la cantidad, por defecto es 1 si no se proporciona
        quantity = request.data.get('quantity', 1)

        # Validamos que se haya proporcionado el ID del producto
        if not product_id:
            return Response({"detail": "El ID del producto es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtenemos el producto correspondiente
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            # Si el producto no existe, devolvemos un error
            return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Verificamos que haya suficiente stock del producto
        if quantity > product.stock:
            return Response(
                {"detail": "La cantidad solicitada es mayor a la disponible."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtenemos o creamos el carrito del usuario
        cart, created = ShoppingCart.objects.get_or_create(user=request.user)

        # Verificamos si el producto ya está en el carrito
        if CartProducts.objects.filter(cart=cart, product=product).exists():
            return Response({"detail": "Este producto ya está en el carrito."}, status=status.HTTP_400_BAD_REQUEST)

        # Agregamos el producto al carrito
        CartProducts.objects.create(cart=cart, product=product, quantity=quantity)

        # Devolvemos una respuesta de éxito
        return Response({"detail": "Producto agregado al carrito."}, status=status.HTTP_201_CREATED)


# Viste que nos permite eliminar un producto del carrito 
class DeleteProductCartUserView(APIView):
    # Indicamos el método de autenticación
    authentication_classes = [JWTAuthentication]
    # Solo los usuarios autenticados pueden acceder a esta vista
    permission_classes = [IsAuthenticated]

    # DELETE: Permite eliminar un producto del carrito del usuario autenticado
    def delete(self, request, product_id):
        try:
            # Obtenemos el carrito del usuario autenticado
            cart = ShoppingCart.objects.get(user=request.user)
        except ShoppingCart.DoesNotExist:
            # Si el carrito no existe, devolvemos un mensaje de error
            return Response({"detail": "El usuario no tiene un carrito."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Obtenemos el producto del carrito según el ID proporcionado
            cart_product = CartProducts.objects.get(cart=cart, product_id=product_id)
        except CartProducts.DoesNotExist:
            # Si el producto no está en el carrito, devolvemos un mensaje de error
            return Response({"detail": "Producto no encontrado en el carrito."}, status=status.HTTP_404_NOT_FOUND)

        # Eliminamos el producto del carrito
        cart_product.delete()

        # Devolvemos una respuesta exitosa sin contenido
        return Response({"detail": "Producto eliminado del carrito."}, status=status.HTTP_204_NO_CONTENT)

