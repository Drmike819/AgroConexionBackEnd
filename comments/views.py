from rest_framework.response import Response
from rest_framework import status
from .serializer import ( 
    NewCommentsSerializers, EditCommentSerializer, CommentSerializer,
)
from .models import Comments
from rest_framework.views import APIView
from products.models import Products
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
# Create your views here.

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
        # LLmamos al serializador para obtener la informacion
        serializer = CommentSerializer(comments_product, many=True)
        # Mensaje de exito
        return Response(serializer.data, status=status.HTTP_200_OK)
            
