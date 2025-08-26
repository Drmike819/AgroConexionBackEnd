from .models import Category, Products, ProductImage, Grades
from rest_framework import serializers

# serializer para tener las categorias en archivo JSON(API)
class SerializerCategories(serializers.ModelSerializer):
    class Meta:
        # indicamo el modelo que deseamos utilizar
        model = Category
        # indicamos lo campos que queremos utilizar
        fields = '__all__'


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
        read_only_fields = ('producer',)
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
class SerializerCategoriesProducs(serializers.ModelSerializer):
    # Añadimos el serializador de productos para mostar todo los productos asociados
    # many=True: Permitimos que el producto tenga varios productos
    # read_only=True: Solo se pueden ver los productos mas no modificarlos
    products = SerializerProducts(source='category_products', many=True, read_only=True)
    class Meta:
        # indicamo el modelo que deseamos utilizar
        model = Category
        # indicamos lo campos que queremos utilizar
        fields = '__all__'
             

# Serializador para rear un calificacion a un producto
class NewRatingProductSerializer(serializers.ModelSerializer):
    # Campo para obtener el producto de la peticion
    product = serializers.PrimaryKeyRelatedField(queryset=Products.objects.all())

    # Indicamos el modelo y los campos a utilizar
    class Meta:
        model = Grades
        fields = ['product', 'rating']

    # Funcion que nos permite validar la informacion enviada
    def validate(self, data):
        product = data.get("product")
        if not product:
            raise serializers.ValidationError({"product": "Debe indicar un producto."})

        # Validar rating
        rating = data.get("rating")
        if rating is None:
            raise serializers.ValidationError({"rating": "Debe indicar su calificación."})
        if rating < 1:
            raise serializers.ValidationError({"rating": "La calificación no puede ser menor a 1."})
        if rating > 5:
            raise serializers.ValidationError({"rating": "La calificación no puede ser mayor a 5."})

        return data

    # Funcion que nos permite crear una nueva calificacion
    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data['product']
        rating = validated_data['rating']

        # Crear o actualizar calificación
        grade, created = Grades.objects.update_or_create(
            user=user,
            product=product,
            defaults={'rating': rating}
        )
        return grade

        