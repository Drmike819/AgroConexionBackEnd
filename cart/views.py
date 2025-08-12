from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from products.models import Products

from .models import FavoriteProducts, ShoppingCart, CartProducts
from .serializer import  FavoriteProductsSerializer,  CartUserSerializer
# Create your views here.


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
        data = request.data
        
        try:
            Products.objects.get(id=data["product"])
        except Products.DoesNotExist:
            return Response({'error': 'El producto no existe'}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = FavoriteProductsSerializer(
            # Enviamos los datos enviados por el cliente (product_id)
            data=request.data,
            # Enviamos también el request completo como contexto para acceder a request.user en el serializador
            context={'request': request}
        )
        # Validamos el serializador
        serializer.is_valid(raise_exception=True)
        favorite = serializer.save()
        return Response({"message": f"El producto {favorite.product.name} se agrego correctamente"}, status=status.HTTP_200_OK)

    
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
                status=status.HTTP_200_OK
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

        # Obtenemos o creamos el carrito del usuario
        cart, created = ShoppingCart.objects.get_or_create(user=request.user)

        # Verificamos si el producto ya está en el carrito
        cart_product, product_created = CartProducts.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'quantity': quantity}
        )

        if not product_created:
            # Si el producto ya existe, aumentamos la cantidad
            new_quantity = cart_product.quantity + quantity
            
            # Verificamos que la nueva cantidad no exceda el stock disponible
            if new_quantity > product.stock:
                return Response(
                    {"detail": f"La cantidad total ({new_quantity}) excede el stock disponible ({product.stock})."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Actualizamos la cantidad
            cart_product.quantity = new_quantity
            cart_product.save()
            
            return Response({
                "detail": "Cantidad del producto actualizada en el carrito.",
                "product_id": product_id,
                "new_quantity": new_quantity
            }, status=status.HTTP_200_OK)
        else:
            # Si es un producto nuevo, verificamos que no exceda el stock
            if quantity > product.stock:
                # Si excede el stock, eliminamos el producto recién creado
                cart_product.delete()
                return Response(
                    {"detail": "La cantidad solicitada es mayor a la disponible."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Devolvemos una respuesta de éxito para producto nuevo
            return Response({
                "detail": "Producto agregado al carrito.",
                "product_id": product_id,
                "quantity": quantity
            }, status=status.HTTP_201_CREATED)


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
        return Response({"detail": "Producto eliminado del carrito."}, status=status.HTTP_200_OK)