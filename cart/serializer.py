from rest_framework import serializers
from products.serializer import SerializerProducts
from .models import FavoriteProducts, CartProducts, ShoppingCart, FavoritesCategories
from products.models import Products, Category
from products.serializer import SerializerProducts, SerializerCategories

# Serializador para agregar un producto a favoritos        
class FavoriteProductsSerializer(serializers.ModelSerializer):
    # Creacion del campo manual 
    product = serializers.PrimaryKeyRelatedField(
        # Validacion en donde verificamos que el id exista 
        queryset=Products.objects.all(), write_only=True
    )
    
    product_detail = SerializerProducts(source='product', read_only=True)

    # Indicamos los campos y el modelo a utilizar
    class Meta:
        model = FavoriteProducts
        fields = ['product', 'product_detail', 'added_at']

    # Validacion del producto
    def validate_product(self, data):
        if not Products.objects.filter(pk=data.pk).exists():
            raise serializers.ValidationError({"error":"El producto que intentas agregar no existe."})
        return data
    
    # Validacion indentificacondo que el producto ya este en favoritos
    def validate(self, data):
        user = self.context['request'].user
        product = data.get("product")

        if FavoriteProducts.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError({"message": "Este producto ya está en tus favoritos."})

        return data

    # Crecion de la instancia
    def create(self, validated_data):
        validated_data["user"] = self.context['request'].user
        favorite_instance = FavoriteProducts.objects.create(**validated_data)
        return favorite_instance



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


# Serializador para añadir una categoria a favoritos
class NewFavoriteCategorySerializer(serializers.ModelSerializer):
    # Campo en donde buscamos la categoria
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True
    )
    # Campo para obtener el detalle de las categorias
    category_detail = SerializerCategories(read_only=True)
    # Indicamos el modelo y los campos a utilizar
    class Meta:
        model = FavoritesCategories
        fields = ['category', 'category_detail', 'added_at']
        
    # Verificaque la categoria exista
    def validate_category(self, data):
        if not Category.objects.filter(pk=data.pk):
            raise serializers.ValidationError({'category': 'La categoria no existe'})
        return data
    # Validamos que la categoria no esta añadida a favoritos
    def validate(self, data):
        user = self.context['request'].user
        category = data.get("category")
        if FavoritesCategories.objects.filter(category=category, user=user):
            raise serializers.ValidationError({'duplicate': 'La categoria ya esta en favoritos'})
        return data
    # Fincion que crear la union 
    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        validated_data["user"] = user
        instance_categoryFavorite = FavoritesCategories.objects.create(**validated_data)
        return instance_categoryFavorite


# Serializador para obtener la informacion de la categorias en favoritos
class FavoritesCategoriesUser(serializers.ModelSerializer):
    # Obtenemos el serializador de la informacion de las categorias
    category = SerializerCategories(read_only=True)
    # Indicamos el modelo y la informacion a utilizar
    class Meta:
        model = FavoritesCategories
        fields = ['id', 'category', 'added_at']
        
        read_only_fields = ['id', 'created_at']
        
    