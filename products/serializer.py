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
    offers = serializers.SerializerMethodField()
    coupon = serializers.SerializerMethodField()
    
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
    
    # Funcion que nos permite Obtener las ofertas 
    def get_offers(self, obj):
        # Obtenemos las ofertas que estan activadas
        offers = obj.offers.filter(active=True)
        # Buscamso las ofertas obteniudas y verificamos que esten activas
        active_offers = [offer for offer in offers if offer.is_active()]
        # Serializamos las ofertas con el serializador
        from offers_and_coupons.serializer import OfferSerializer
        # Retornamos la informascion serializada
        return OfferSerializer(active_offers, many=True).data
    
    # Funcion para obtener los cupones 
    def get_coupon(self, obj):
        # Obtenemos los cupones que esten activos
        coupon = obj.coupons.filter(active=True)
        # Recorremos la lista y verificamos que esten activos
        active_coupon = [coupon for coupon in coupon if coupon.is_active()]
        # Serializamos y retornamos la inofrmacion
        from offers_and_coupons.serializer import CouponSerializer
        return CouponSerializer(active_coupon, many=True).data


# Serializador para editar un producto 
class EditProductSerializer(serializers.ModelSerializer):
    # Variable que almacenará las nuevas imágenes
    images = serializers.ListField(
        child=serializers.ImageField(max_length=None, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    # Lista en donde almacenaremos los ID de las imágenes que queremos eliminar 
    delete_images = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    # Para mostrar las imágenes existentes (solo lectura)
    current_images = serializers.SerializerMethodField(read_only=True)

    # Indicamos el modelo y los campos a utilizar
    class Meta:
        model = Products
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock",
            "unit_of_measure",
            "category",
            "producer",
            "date_of_registration",
            "state",
            "images",
            "delete_images",
            "current_images"
        ]
        # Campos que no se pueden editar
        read_only_fields = ["id","producer", "date_of_registration"]

    # Funcion para obtener la imagenes del producto
    def get_current_images(self, obj):
        return [
            {"id": image.id, "image": image.image.url}
            for image in obj.images.all()
        ]

    # Funcion para actualizar el producto
    def update(self, instance, validated_data):
        # Obtenemos las imagenes nuevas 
        new_images = validated_data.pop("images", [])
        # Obtenemos losd ids de las imagenes a eliminar
        delete_images_ids = validated_data.pop("delete_images", [])
        # Obtenemos las categorias enviadas por el usuario
        categories_data = validated_data.pop("category", None)

        # Actualizamos los campos del producto
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizamos y remplaza las categorias
        if categories_data is not None:
            instance.category.set(categories_data)

        # Agrga lasnuevam s iamgenes del usuario
        for image in new_images:
            ProductImage.objects.create(product=instance, image=image)

        # Elimina las imagenes selecionadas
        if delete_images_ids:
            ProductImage.objects.filter(id__in=delete_images_ids, product=instance).delete()

        return instance

                   
# serializer para tener las categorias en archivo JSON(API)
class SerializerCategoriesProducs(serializers.ModelSerializer):
    # Añadimos el serializador de productos para mostar todo los productos asociados
    # many=True: Permitimos que el producto tenga varios productos
    # read_only=True: Solo se pueden ver los productos mas no modificarlos
    products = serializers.SerializerMethodField()
    class Meta:
        # indicamo el modelo que deseamos utilizar
        model = Category
        # indicamos lo campos que queremos utilizar
        fields = '__all__'
    
        # Método para obtener y serializar solo los productos que no sean 'inactivo'
    def get_products(self, obj):
        # Filtramos los productos de la categoría actual excluyendo los que tienen 'state' como 'inactivo'
        products = obj.category_products.exclude(state='inactivo')
        
        # Luego serializamos los productos filtrados
        return SerializerProducts(products, many=True).data
             

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

        