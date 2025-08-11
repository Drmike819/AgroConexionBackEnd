from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .serializer import (
    SerializerCategories, 
    SerializerProducts, SerializerCategoriesProducs, 
    NewCommentsSerializers, EditCommentSerializer, CommentSerializer,
    NewRatingProduct,
)

from rest_framework.views import APIView
from .models import Category, Products, Comments, Grades
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# Create your views here.

# creacion de la (API) para obtener todas las categorias
class CategoriesView(APIView):
    # indicamos los permisos que necesita la API
    permission_classes = [AllowAny]
    # solicitud con el metodo get
    def get(self, request, *args, **kwargs):
        # nos devuel las instancias del todas las categorias
        categories = Category.objects.all()
        # convertimos las categorias en un formato JSON y inidcamo sque tendremos mas de una categoria
        serializer = SerializerCategories(categories, many=True)
        # retornamos la informacion del serializer (JSON)
        # print(serializer.data)
        return Response(serializer.data)


# View en donde se muestran los productos de una categoria especifica
class ProducsCategoriesView(APIView):
    # Permisos de la clase
    permission_classes = [AllowAny]
    
    # Funcion en donde obtenemos a la categoria
    def get_object(self, category_id):
        try:
            # Retornamos la categoria
            return Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            # Retornamos None
            return None
    
    # Method GET
    def get(self, request, category_id, *args, **kwargs):
        # Obtenemos la categoria
        category = self.get_object(category_id)
        # Verificamos que la categoria exista
        if not category:
            return Response({'error': 'La categoria no a sido encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        # Obtenemos los productos cuya categoria sea la buscada
        products = Products.objects.filter(category=category.id)
        
        # Verificamos que existan productos en esta categoria
        if not products.exists():
            return Response({'message': f'La categoria {category.name} no tiene productos asignados'})
        
        # Obtenemnos la data 
        serializer = SerializerCategoriesProducs(category)
        # Retornamos la informacion 
        return Response(serializer.data, status=status.HTTP_200_OK)
        

# creacion de la (API) para obtener todos los productos     
class ProducstView(APIView):
    # indicamos los permisos que necesita API
    permission_classes = [AllowAny]
    
    # Si el metodo de solicitud es get
    def get(self, request, *args, **kwargs):
        # obtenemos todos los objetos del modelo y lo almacenamos en una variable
        products = Products.objects.all()
        # llamamos al serializador indicando la variable en donde tenemos todos los objetos del modelo
        # many=True: indicamos que hay mas de un modelo
        serializer = SerializerProducts(products, many=True)
        # retornamos el serializador con toda la informacion
        return Response(serializer.data) 


# Vista para obtener solo los productos del usuario logueado
class UserProductsView(APIView):
    # Solo los usuarios con token JWT pueden acceder
    authentication_classes = [JWTAuthentication]
    # Solo usuarios autenticados pueden acceder
    permission_classes = [IsAuthenticated]
    
    # Metodo get
    def get(self, request, *args, **kwargs):

        # Obtenemos el usuario de la petición
        user = request.user
        
        # Filtramos los productos por el usuario logueado (producer)
        user_products = Products.objects.filter(producer=user)
        
        # Verificamos si el usuario tiene productos
        if not user_products.exists():
            return Response(
                {'message': 'No tienes productos registrados aún'}, 
                status=status.HTTP_200_OK
            )
        
        # Serializamos los productos del usuario
        serializer = SerializerProducts(user_products, many=True)
        
        # Retornamos los productos con información adicional
        return Response({
            'user_id': user.id,
            'username': user.username,
            'total_products': user_products.count(),
            'products': serializer.data
        }, status=status.HTTP_200_OK)
        

# creacion de la (API) para obtener la informacion de un producto en concreto
class DetailProductView(APIView):
    # indicamos los permisos que solicita la API
    permission_classes = [AllowAny]
    
    # Funcion que nos permite obtener el id de un producto
    def get_object(self, product_id):
        # capturacion de errores
        try:
            # si el id existe retornamos el oibjeto con el id
            return Products.objects.get(id = product_id)
        except Products.DoesNotExist:
            # si no existe retornamos none
            return None
    
    # si el metodo es get
    def get(self, request, product_id, *args, **kwargs):
        # almacenamos la funcion para obtener un producto en una variable
        product = self.get_object(product_id)
        # verificamos el valor obtenido por la funcion
        if not product:
            # en caso de que no exista retornamos un mensaje
            return Response({'rest': 'Producto no disponible'})
        # en casoi de que exista llamamos a serializer y le indicamos el objeto en concreto que serializara
        serializer = SerializerProducts(product)
        # retornamos la informacion del serializer y un mensdaje HTTP
        return Response(serializer.data, status=status.HTTP_200_OK)


# creacion de la API para crear un nuevo producto
class NewProductosView(APIView):
    
    # solo los usuraios con el token JWT pueden acceder a esta 
    authentication_classes = [JWTAuthentication]
    # indicamos que las personas autenticadas son los unicos que pueden acceder a esta
    permission_classes = [IsAuthenticated]

    # funcion que nos permite subir el producto a la base de datos
    def post(self, request, *args, **kwargs):
        # obtenemos la iformacion de usuario
        user = request.user
        # copias la informacion del usuario
        data = request.data.copy()
        # inidcamos que el id del usuario sera el productos del producto creado
        data['producer'] = user.id

        # limpieza de datos, asegura que los datos enciados sean los requeridos en la base de datos
        price = float(data.get('price', 0))
        stock = int(data.get('stock', 0))

        # verifica que el precio no sea menor o igual a 0 y que el stock no sea menor a 0
        if price <= 0 or stock < 0:
            # en caso de error retornamos un mensaje de error
            return Response({"detail": "El precio debe ser mayor a 0 y el stock no puede ser negativo"}, status=status.HTTP_400_BAD_REQUEST)

        # verificamos el campo categorias y la informacion enviada en el
        if 'category' in data:
            try:
                # obtenemos la informacion enviado y la volvemos una lista de categorias,
                # cambias los valores string en valor numericos, y guardamo sla nueva lista con los valores remplazados
                data.setlist('category', [int(cat_id) for cat_id in data.getlist('category')])
            # si algun valor no sepuede comvertir a numerico mandamo suna VValueError
            except ValueError:
                # mensaje de error
                return Response({"category": ["Formato inválido. Se espera una lista de IDs numéricos."]}, status=status.HTTP_400_BAD_REQUEST)

        # serializador para verificar los datos
        serializer = SerializerProducts(data=data)
        # si el serializador es correcto 
        if serializer.is_valid():
            # guarda el nuevo producto en la base de datos
            producto = serializer.save()
            # las imagenes enviadas en el formulario se asocian al nuevo producto
            images = request.FILES.getlist('images')
            for image in images:
                producto.images.create(image=image)
            # mensaje de exito
            return Response({"detail": "Producto creado correctamente"}, status=status.HTTP_201_CREATED)
        # mensaje de error
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View que permite editar un producto
class EditProductView(APIView):
    # Solo los usuarios con token JWT pueden acceder
    authentication_classes = [JWTAuthentication]
    # Solo usuarios autenticados pueden acceder
    permission_classes = [IsAuthenticated]
    
    def get_object(self, product_id, user):
        """
        Función para obtener un producto específico verificando que el usuario sea el creador
        """
        try:
            # Verificamos que el producto existe Y que el usuario logueado sea el creador
            return Products.objects.get(id=product_id, producer=user)
        except Products.DoesNotExist:
            return None
    
    def put(self, request, product_id, *args, **kwargs):
        """
        Actualizar un producto existente
        """
        # Obtenemos el producto verificando que sea del usuario logueado
        product = self.get_object(product_id, request.user)
        
        if not product:
            return Response(
                {'detail': 'Producto no encontrado o no tienes permisos para editarlo'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Copiamos los datos de la petición
        data = request.data.copy()
        
        # Si los datos vienen dentro de 'current_product', los extraemos
        if 'current_product' in data:
            data = data['current_product'].copy()
        
        # Limpieza de datos
        try:
            price = float(data.get('price', product.price))
            stock = int(data.get('stock', product.stock))
        except (ValueError, TypeError):
            return Response(
                {"detail": "Formato inválido en precio o stock"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificamos que el precio y stock sean válidos
        if price <= 0 or stock < 0:
            return Response(
                {"detail": "El precio debe ser mayor a 0 y el stock no puede ser negativo"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Procesamos las categorías si se enviaron
        if 'category' in data:
            try:
                # Verificamos si data es un QueryDict (form-data) o dict (JSON)
                if hasattr(data, 'getlist'):
                    # Es un QueryDict (form-data)
                    data.setlist('category', [int(cat_id) for cat_id in data.getlist('category')])
                else:
                    # Es un dict normal (JSON)
                    categories = data.get('category', [])
                    if isinstance(categories, list):
                        # Ya es una lista, solo convertimos a enteros
                        data['category'] = [int(cat_id) for cat_id in categories]
                    else:
                        # Es un solo valor, lo convertimos a lista
                        data['category'] = [int(categories)]
            except (ValueError, TypeError):
                return Response(
                    {"category": ["Formato inválido. Se espera una lista de IDs numéricos."]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Utilizamos el serializer para validar y actualizar los datos
        serializer = SerializerProducts(product, data=data, partial=True)
        
        if serializer.is_valid():
            # Guardamos los cambios
            producto_actualizado = serializer.save()
            
            # Si se enviaron nuevas imágenes, las agregamos
            images = request.FILES.getlist('images')
            for image in images:
                producto_actualizado.images.create(image=image)
            
            return Response(
                {"detail": "Producto actualizado correctamente", "product": serializer.data}, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Crear una vista separada para eliminar productos
class DeleteProductView(APIView):
    # Solo los usuarios con token JWT pueden acceder
    authentication_classes = [JWTAuthentication]
    # Solo usuarios autenticados pueden acceder
    permission_classes = [IsAuthenticated]
    
    def get_object(self, product_id, user):
        """
        Función para obtener un producto específico verificando que el usuario sea el creador
        """
        try:
            # Verificamos que el producto existe Y que el usuario logueado sea el creador
            return Products.objects.get(id=product_id, producer=user)
        except Products.DoesNotExist:
            return None
    
    def delete(self, request, product_id, *args, **kwargs):
        """
        Eliminar un producto - solo si el usuario es el creador
        """
        # Obtenemos el producto verificando que sea del usuario logueado
        product = self.get_object(product_id, request.user)
        
        if not product:
            return Response(
                {'detail': 'Producto no encontrado o no tienes permisos para eliminarlo'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Guardamos el nombre del producto para el mensaje de confirmación
        product_name = product.name
        
        # Eliminamos el producto
        product.delete()
        
        return Response(
            {'detail': f'Producto "{product_name}" eliminado correctamente'}, 
            status=status.HTTP_200_OK
        )
        
 
# View que nos permite crear un nuevo comentario    
class NewCommentView(APIView):
    # Solo los usuarios con token JWT pueden acceder
    authentication_classes = [JWTAuthentication]
    # Solo usuarios autenticados pueden acceder
    permission_classes = [IsAuthenticated]
    
    # Methdo POST
    def post(self, request, *args, **kwargs):
        # Obtenemos el serializador y le pasamos la informacion de la peticion
        serializer = NewCommentsSerializers(data=request.data, context={"request":request})
        # Validamos el serializador
        serializer.is_valid(raise_exception=True)
        # Guardamos la instancia creada
        comment = serializer.save()

        # Retornar respuesta
        return Response({"message": f"Se añadio correctamente el commentario al producto: {comment.product.name}"}, status=status.HTTP_201_CREATED)
    

# View que nos permite editar un comentario
class EditCommentView(APIView):
    # Solo los usuarios con token JWT pueden acceder
    authentication_classes = [JWTAuthentication]
    # Solo usuarios autenticados pueden acceder
    permission_classes = [IsAuthenticated] 
    
    # funcion que nos permite Obtener el comentario 
    def get_object(self, comment_id, user):
        
        try:
            # Retornamos el comentario
            return Comments.objects.get(id=comment_id, user=user)
        except Comments.DoesNotExist:
            # En caso de no encontrarlo retornamos None
            return None   
        
    # Method PUT
    def put(self, request, comment_id, *args, **kwargs):
        # Guardamos la repuesta de la funcion
        comment = self.get_object(comment_id, request.user)
        # Verificamos que exista el comentario
        if not comment:
            return Response({"error": "Comentario no encontrado o no tienes permiso para editarlo."}, status=status.HTTP_404_NOT_FOUND)
        
        # Obtenemos el serializador y le pasamos la informacion
        serializer = EditCommentSerializer(comment, data=request.data, context={"request": request}, partial=True)
        # Validamos el serializador
        serializer.is_valid(raise_exception=True)
        # Guardamos el comentario editado
        edit_comment = serializer.save()

        return Response({"message": f"Comentario del producto '{edit_comment.product.name}' actualizado correctamente."}, status=status.HTTP_200_OK)
    

# View quenos permite eliminar un comentario
class DeleteCommnetView(APIView):
    # Solo los usuarios con token JWT pueden acceder
    authentication_classes = [JWTAuthentication]
    # Solo usuarios autenticados pueden acceder
    permission_classes = [IsAuthenticated] 
    
    # Funcion que nos permite obtener el comentario
    def get_object(self, comment_id, user):
        
        try:
            # Retornamos el comentario
            return Comments.objects.get(id=comment_id, user=user)
        except Comments.DoesNotExist:
            # Retornamos none
            return None
    
    # Method DELETE
    def delete(self, request, comment_id, *args, **kwargs):
        # Obtenemos el comentario
        commnet = self.get_object(comment_id, user=request.user)
        # Validamos que el comentario exista
        if not commnet:
            return Response({"error": "Comentario no encontrado o no tienes permiso para eliminarla"}, status=status.HTTP_404_NOT_FOUND)
        # Eliminamos el comentario
        commnet.delete()
        # Respuesta de exito
        return Response({'message':'El comentario fue eliminado correctamente'},status=status.HTTP_200_OK)
    

# View que nos permite obtenero los comentarios de un usuario en concreto
class CommentsProduct(APIView):
    # Todos pueden acceder
    permission_classes = [AllowAny]
    
    # Funcion que os permite obtener un producto en especifico
    def get_object(self, product_id):
        try:
            # Obtenemos el producto y lo retornamos
            return Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            # Retornamos None
            return None
        
    # Method GET
    def get(self, request, product_id, *args, **kwargs):
        # Obtenemos el producto
        product = self.get_object(product_id)
        # Veridicamso que el producto exista
        if not product:
            return Response({"error": "El producto no ha sido encontrado"})
        
        # Obtenemos lso comentarios del poroducto obtenido
        comments_product = Comments.objects.filter(product=product.id)
        
        # Verificamos que axistan comentarios 
        if not comments_product.exists():
            return Response(
                {'message': 'Este producto no tiene comentarios aun'}, 
                status=status.HTTP_200_OK
            )
        # LLmamos al serializador para obtener la informacion
        serializer = CommentSerializer(comments_product, many=True)
        # Mensaje de exito
        return Response(serializer.data, status=status.HTTP_200_OK)
            

#
class NewRatingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = NewRatingProduct(data=request.data, context={"request": request})
        if serializer.is_valid():
            rating = serializer.save()
            return Response(
                {'message': f'Se ha calificado con éxito el producto {rating.product.name} con {rating.rating} estrellas.'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#
class DeleteRatingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_object(self, grade_id, user):
        try:
            return Grades.objects.get(id=grade_id, user=user)
        except Grades.DoesNotExist:
            return None
    def delete(self, request, grade_id, *args, **kwargs):
        grade = self.get_object(grade_id, user=request.user)
        if not grade:
            return Response({"error": "Calificacion no encontrado o no tienes permiso para eliminarla"}, status=status.HTTP_404_NOT_FOUND)
        # Eliminamos el comentario
        grade.delete()
        # Respuesta de exito
        return Response({'message':'La calificacion fue eliminado correctamente'},status=status.HTTP_200_OK)


#
class EstatsGradesView(APIView):
    permission_classes = [AllowAny]
    
    def get_object(self, product_id):
        try:
            return Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return None
    
    def get(self, request, product_id, *args, **kwargs):
        product = self.get_object(product_id)
        
        if not product:
            return Response({"error": "El producto no ha sido encontrado"})
        
        ratings_data = (
            Grades.objects
            .filter(product=product_id)
            .values("rating")
            .annotate(count=Count("rating"))
        )

        # Calcular total
        total_ratings = sum(item["count"] for item in ratings_data)

        # Construir respuesta con 1 a 5 estrellas
        stats = []
        for star in range(1, 6):
            count = next((item["count"] for item in ratings_data if item["rating"] == star), 0)
            percentage = (count / total_ratings * 100) if total_ratings > 0 else 0
            stats.append({
                "star": star,
                "count": count,
                "percentage": round(percentage, 2)
            })

        return Response({
            "product_id": product_id,
            "total_ratings": total_ratings,
            "stars": stats
        }, status=status.HTTP_200_OK)
        
        