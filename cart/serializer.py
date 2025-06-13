from rest_framework import serializers
from products.serializer import SerializerProducts
from .models import FavoriteProducts, CartProducts, ShoppingCart

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


# Serializador para los productos en el carrito
class CartProductsUserSerializer(serializers.ModelSerializer):
    # Usamos el serializador de productos para mostrar su información detallada
    product = SerializerProducts(read_only=True)

    class Meta:
        # Indicamos el modelo que se va a serializar
        model = CartProducts
        # Campos que se incluirán en la representación
        fields = ['id', 'product', 'quantity']
        # El campo 'id' no podrá ser modificado por el usuario
        read_only_fields = ['id']


# Serializador para el carrito del usuario
class CartUserSerializer(serializers.ModelSerializer):
    # Utilizamos el serializador previamente definido para mostrar los productos del carrito del usuario autenticado
    products = CartProductsUserSerializer(read_only=True, many=True)

    class Meta:
        # Indicamos el modelo que se va a serializar
        model = ShoppingCart
        # Campos que se incluirán en la representación
        fields = ['id', 'created_at', 'products']
        # Los campos 'id' y 'created_at' no pueden ser modificados por el cliente
        read_only_fields = ['id', 'created_at']