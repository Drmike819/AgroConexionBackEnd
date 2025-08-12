from .models import Category, Products, ProductImage, CommentsImage, Comments, Grades, Offers
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
        
        
# Serializador que nos permite obtener las imagenes de los comentarios
class CommentsImgesSerializer(serializers.ModelSerializer):
    
    class Meta:
        # Definimos el modelo a utilizar
        model = CommentsImage
        # Definimo slos campos que utilizaremos
        fields = ["id", "image"]      
        

# Serializador que nos permite crear un nuevo comnetario
class NewCommentsSerializers(serializers.ModelSerializer):
    # Variable en donde almacenaremos una lista de imagenes 
    images = serializers.ListField(
        # Indicamos que sera una lista de imagenes
        child=serializers.ImageField(max_length=None, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        # Indicamos el modelo a utilizar
        model = Comments
        # Indicamos lso campos que utilizaremos
        fields = ["id", "product", "comment", "images"]

    # Funcion qu enos permite validar la data
    def validate(self, data):
        # Validar que el producto exista
        product = data.get("product")
        if not product or not Products.objects.filter(id=product.id).exists():
            raise serializers.ValidationError({"product": "El producto no existe."})

        # Validar que el comentario no esté vacío
        comment = data.get("comment")
        if not comment or comment.strip() == "":
            raise serializers.ValidationError({"coments": "El comentario no puede estar vacío."})

        # Retornamos la informacion
        return data

    # Funcion qu enos permite crear la instancia del comentario
    def create(self, validated_data):
        
        request = self.context.get("request")

        # Extraer imágenes si vienen en la petición
        images_data = validated_data.pop("images", [])

        # Asignar el usuario autenticado
        validated_data["user"] = request.user

        # Crear el comentario
        comment_instance = Comments.objects.create(**validated_data)

        # Crear las imágenes relacionadas
        for image in images_data:
            CommentsImage.objects.create(comment=comment_instance, image=image)

        # Retornamos el objeto creado
        return comment_instance


# Serializador para editar un comentario
class EditCommentSerializer(serializers.ModelSerializer):
    
    # Variable que almacenara la imagenes nuevas
    images = serializers.ListField(
        child=serializers.ImageField(max_length=None, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )   
     
    # Lista en donde alamcenaremos los id's de las images ue queremos eliminar 
    delete_images = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        # Indicamos el modelo que utilizaremos
        model = Comments
        # Campos que utilizaresmos
        fields = ["comment", "images", "delete_images"]

    def validate(self, data):
        # Verificamos que en la solicitud envien el campo comment
        if "comment" in data:
            # Guardamos la informacion enviada
            comment = data["comment"]
            # Validar que el comentario no esté vacío
            if not comment or comment.strip() == "":
                raise serializers.ValidationError({"error": "El comentario no puede estar vacío."})
        # Retornamos el objeto
        return data
    
    # Funcion que nso permite actuazlizar el objeto
    def update(self, instance, validated_data):
        # Actualizar el texto del comentario en caso de que se enviara el la dta
        instance.comment = validated_data.get("comment", instance.comment)
        # Guardamos el commentario
        instance.save()

        # Agregar nuevas imágenes
        images_data = validated_data.get("images", [])
        for image in images_data:
            CommentsImage.objects.create(comment=instance, image=image)

        # Eliminar imágenes seleccionadas
        delete_images_ids = validated_data.get("delete_images", [])
        if delete_images_ids:
            CommentsImage.objects.filter(id__in=delete_images_ids, comment=instance).delete()

        # Retornamos el objeto actualizado
        return instance
    

# Serializer que nos permite imprimir la informacion de os comentarios con sus imagenes
class CommentSerializer(serializers.ModelSerializer):
    # Obtenemos la images del serializador
    images = CommentsImgesSerializer(many=True, read_only=True)
    # Indicamos el modelo a autilizar y sus campos
    class Meta:
        model = Comments
        fields = '__all__'
        

#
class NewRatingProduct(serializers.ModelSerializer):
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
class NewOffert(serializers.ModelSerializer):
    product = serializers.IntegerField()
    
    class Meta:
        model = Offers
        fields = ['product', 'title', 'description', 'percentage', 'start_date', 'end_date']
    
    def validate(self, data):
        producto_id = data.get("product")
        
        if not producto_id:
            raise serializers.ValidationError({"error": "El producto es necesario"})
        
        try:
            product = Products.objects.get(id=producto_id)
        except Products.DoesNotExist:
            raise serializers.ValidationError({"product": "El producto no existe."})
        
        title = data.get("title")
        if not title:
            raise serializers.ValidationError({"error": "El titulo es obligatorio"})
        
        description = data.get("description")
        if not description:
            raise serializers.ValidationError({"error": "La descripcion es obligatorio"})
        
        percentage = data.get("percentage")
        if percentage < 1 or percentage > 100:
            raise serializers.ValidationError({"error": "El porcentaje de descuento debe estar entre 1 y 100."})

        if percentage.as_tuple().exponent < -2:  
            raise serializers.ValidationError({"error": "El porcentaje solo puede tener hasta dos decimales."})
        
        
        start_date = data.get('start_date', timezone.now())
        end_date = data.get('end_date')
        
        if start_date < timezone.now():
            raise serializers.ValidationError({"error": "La fecha de inicio no puede ser menor a la fecha actual."})
        
        if end_date and end_date < start_date:
            raise serializers.ValidationError({"error": "La fecha de fin no puede ser menor que la fecha de inicio."})
        
        # Reemplazar el ID por la instancia
        data["product"] = product
        return data
        
    def create(self, validate_data):
        request = self.context['request']
        user = self.context['request'].user
        