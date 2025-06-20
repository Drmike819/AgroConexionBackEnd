from .models import Category, Products, ProductImage
from rest_framework import serializers


# creacion del serializer de las imagenes de los productos    
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        # indicamo el modelo que deseamos utilizar
        model = ProductImage
        # indicamos los campos que serializaremos
        fields = ['id', 'image'] 
        

# Creación del serializer para obtener todos los productos
class SerializerProducts(serializers.ModelSerializer):
    # Añadimos el serializador de imágenes del producto para mostrar todas las imágenes asociadas
    # many=True: Permitimos que el producto tenga varias imágenes
    # read_only=True: Solo se pueden ver las imágenes, no modificarlas desde este serializer
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        # Indicamos el modelo que deseamos utilizar
        model = Products
        # Serializamos todos los campos del modelo
        fields = '__all__'
    
        # funcion personalizada para validar el precio
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0")
        return value

    # funcion personalizada para validar el stock
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo")
        return value

               
# serializer para tener las categorias en archivo JSON(API)
class SerializerCategories(serializers.ModelSerializer):
    # Añadimos el serializador de productos para mostar todo los productos asociados
    # many=True: Permitimos que el producto tenga varios productos
    # read_only=True: Solo se pueden ver los productos mas no modificarlos
    products = SerializerProducts(source='category_products', many=True, read_only=True)
    class Meta:
        # indicamo el modelo que deseamos utilizar
        model = Category
        # indicamos lo campos que queremos utilizar
        fields = '__all__'
        

# # creacion del serializadoe para crear un nuevo producto
# class NewProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         # indicamos el modelo que utilizaremos
#         model = Products
#         # indicamos los campos a utilizar
#         fields = '__all__'

#     # funcion personalizada para validar el precio
#     def validate_price(self, value):
#         if value <= 0:
#             raise serializers.ValidationError("El precio debe ser mayor a 0")
#         return value

#     # funcion personalizada para validar el stock
#     def validate_stock(self, value):
#         if value < 0:
#             raise serializers.ValidationError("El stock no puede ser negativo")
#         return value