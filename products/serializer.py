from .models import Category, Products, ProductImage, Grades, Offers
from rest_framework import serializers

from django.utils import timezone
from datetime import timedelta

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
             

#
class NewRatingProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Products.objects.all())

    class Meta:
        model = Grades
        fields = ['product', 'rating']

    def validate(self, data):
        request = self.context['request']

        # Validar producto
        product_id = data.get("product")
        if not product_id:
            raise serializers.ValidationError({"product": "Debe indicar un producto."})

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            raise serializers.ValidationError({"product": "El producto no existe."})

        # Validar rating
        rating = data.get("rating")
        if rating is None:
            raise serializers.ValidationError({"rating": "Debe indicar su calificación."})
        if rating < 1:
            raise serializers.ValidationError({"rating": "La calificación no puede ser menor a 1."})
        if rating > 5:
            raise serializers.ValidationError({"rating": "La calificación no puede ser mayor a 5."})

        # Reemplazar el ID por la instancia
        data["product"] = product

        return data

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


#
class NewOffertSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Products.objects.all(),
        write_only=True
    )
    # Campo de solo lectura para devolver los datos del producto
    product_detail = SerializerProducts(source='product', read_only=True)
    
    class Meta:
        model = Offers
        fields = ['product', 'product_detail', 'title', 'description', 'percentage', 'start_date', 'end_date']
    
    def validate(self, data):
        product = data.get("product")  # Ya es una instancia de Products
        user = self.context['request'].user

        if product.producer != user:
            raise serializers.ValidationError({
                "product": "El producto no existe o no tienes permisos en este."
            })

        title = data.get("title")
        if not title:
            raise serializers.ValidationError({"error": "El titulo es obligatorio"})

        description = data.get("description")
        if not description:
            raise serializers.ValidationError({"error": "La descripcion es obligatorio"})

        percentage = data.get("percentage")
        if percentage < 1 or percentage > 100:
            raise serializers.ValidationError({
                "error": "El porcentaje de descuento debe estar entre 1 y 100."
            })

        if percentage.as_tuple().exponent < -2:
            raise serializers.ValidationError({
                "error": "El porcentaje solo puede tener hasta dos decimales."
            })

        start_date = data.get('start_date', timezone.now())
        end_date = data.get('end_date')

        if start_date < timezone.now():
            raise serializers.ValidationError({
                "error": "La fecha de inicio no puede ser menor a la fecha actual."
            })

        if end_date and end_date < start_date:
            raise serializers.ValidationError({
                "error": "La fecha de fin no puede ser menor que la fecha de inicio."
            })

        return data

        
    def create(self, validate_data):
        request = self.context['request']
        validate_data['seller'] = request.user
        
        offer_instance = Offers.objects.create(**validate_data)
        
        return offer_instance
        