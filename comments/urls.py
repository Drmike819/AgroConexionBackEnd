from django.urls import path
from .views import (
    NewCommentView, EditCommentView, DeleteCommnetView, CommentsProduct,
)
# url de la aplicacion (users)
urlpatterns = [
    # URLS  
    path('product-comments/<int:product_id>/', CommentsProduct.as_view(), name='comentarios_producto'),
    path('new-comment/', NewCommentView.as_view(), name='nuevo_comentario'),
    path('edit-comment/<int:comment_id>/', EditCommentView.as_view(), name='editar_comentario'),
    path('delete-comment/<int:comment_id>/', DeleteCommnetView.as_view(), name='eliminar_comentario')
]