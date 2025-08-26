from rest_framework import serializers
from .models import Comments, CommentsImage
from products.models import Products
from users.models import CustomUser
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
    
class CommentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'profile_image']
        
# Serializer que nos permite imprimir la informacion de os comentarios con sus imagenes
class CommentSerializer(serializers.ModelSerializer):
    # Obtenemos la images del serializador
    images = CommentsImgesSerializer(many=True, read_only=True)
    user = CommentUserSerializer(read_only=True)
    # Indicamos el modelo a autilizar y sus campos
    class Meta:
        model = Comments
        fields = '__all__'