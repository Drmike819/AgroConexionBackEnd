from rest_framework.response import Response
from rest_framework import status
from .serializer import SerializerCategories, SerializerProducts, SerializerCategoriesProducs
from rest_framework.views import APIView
from .models import Category, Products
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
    
    
# creacion de la (API) para obtener todas las categorias con sus productos
class ProducsCategoriesView(APIView):
    # indicamos los permisos que necesita la API
    permission_classes = [AllowAny]
    # solicitud con el metodo get
    def get(self, request, *args, **kwargs):
        # nos devuel las instancias del todas las categorias
        categories = Category.objects.all()
        # convertimos las categorias en un formato JSON y inidcamo sque tendremos mas de una categoria
        serializer = SerializerCategoriesProducs(categories, many=True)
        # retornamos la informacion del serializer (JSON)
        # print(serializer.data)
        return Response(serializer.data)
        

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
class FormProductosView(APIView):
    
    # solo los usuraios con el token JWT pueden acceder a esta 
    authentication_classes = [JWTAuthentication]
    # indicamos que las personas autenticadas son los unicos que pueden acceder a esta
    permission_classes = [IsAuthenticated]

    # con el metodo get enviamos los campos del formulario para la creacion de un nuevo producto
    def get(self, request, *args, **kwargs):
        # alamacenamos las opciones de unidad encontradas en el modelo
        unit_choices = [{'value': key, 'label': value} for key, value in Products.UNIT_CHOICES]
        # obtenemos todas las instacias creadas del modelo categorias 
        categorias = Category.objects.all()
        # obtenemos todos las categorias 
        opciones_categorias = [{'value': categoria.id, 'label': categoria.name} for categoria in categorias]

        # campos del formulario que deseamos utilizar para la creacion de una nuevo producto
        fields = [
            {"name": "name", "label": "Nombre del producto", "type": "text", "required": True},
            {"name": "description", "label": "Descripción del producto", "type": "text", "required": True},
            {"name": "price", "label": "Precio del producto", "type": "number", "step": "0.01", "required": True},
            {"name": "stock", "label": "Cantidad disponible", "type": "number", "step": "1", "required": True},
            {"name": "unit_of_measure", "label": "Unidad de medida", "type": "select", "options": unit_choices, "required": True},
            {"name": "images", "label": "Imágenes del producto", "type": "file", "multiple": True, "required": False},
            {"name": "category", "label": "Categoría", "type": "select", "options": opciones_categorias, "multiple": True, "required": True},
        ]
        # retornamos los campos
        return Response({"fields": fields})

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

# Agregar esta vista a tu archivo views.py

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
    
    def get(self, request, product_id, *args, **kwargs):
        """
        Obtener los datos actuales del producto para pre-llenar el formulario de edición
        """
        # Obtenemos el producto verificando que sea del usuario logueado
        product = self.get_object(product_id, request.user)
        
        if not product:
            return Response(
                {'detail': 'Producto no encontrado o no tienes permisos para editarlo'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Opciones para los campos select
        unit_choices = [{'value': key, 'label': value} for key, value in Products.UNIT_CHOICES]
        status_choices = [{'value': key, 'label': value} for key, value in Products.STATUS_CHOICES]
        
        # Obtenemos todas las categorías disponibles
        categorias = Category.objects.all()
        opciones_categorias = [{'value': categoria.id, 'label': categoria.name} for categoria in categorias]
        
        # Campos del formulario con los datos actuales del producto
        fields = [
            {"name": "name", "label": "Nombre del producto", "type": "text", "required": True, "value": product.name},
            {"name": "description", "label": "Descripción del producto", "type": "text", "required": True, "value": product.description},
            {"name": "price", "label": "Precio del producto", "type": "number", "step": "0.01", "required": True, "value": str(product.price)},
            {"name": "stock", "label": "Cantidad disponible", "type": "number", "step": "1", "required": True, "value": product.stock},
            {"name": "unit_of_measure", "label": "Unidad de medida", "type": "select", "options": unit_choices, "required": True, "value": product.unit_of_measure},
            {"name": "state", "label": "Estado del producto", "type": "select", "options": status_choices, "required": True, "value": product.state},
            {"name": "images", "label": "Nuevas imágenes del producto", "type": "file", "multiple": True, "required": False},
            {"name": "category", "label": "Categoría", "type": "select", "options": opciones_categorias, "multiple": True, "required": True, "value": list(product.category.values_list('id', flat=True))},
        ]
        
        # Serializamos el producto actual para obtener toda su información
        serializer = SerializerProducts(product)
        
        return Response({
            "fields": fields,
            "current_product": serializer.data
        })
    
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