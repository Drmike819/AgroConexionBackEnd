from django.urls import path
from .views import (
    CategoriesView, ProducsCategoriesView, 
    ProducstView, DetailProductView, NewProductosView, EditProductView, DeleteProductView, UserProductsView, 
    NewCommentView, EditCommentView, DeleteCommnetView, CommentsProduct
)
# url de la aplicacion (users)
urlpatterns = [
    # URLS
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('categories/<int:category_id>/', ProducsCategoriesView.as_view(), name='products_categories'),
    
    path('list-products/', ProducstView.as_view(), name='Products'),
    path('my-products/', UserProductsView.as_view(), name="mis_productos" ),
    path('product/<int:product_id>/', DetailProductView.as_view(), name='Detail_product'),
    path('new-product/', NewProductosView.as_view(), name='formulario_producto'),
    path('edit-product/<int:product_id>/', EditProductView.as_view(), name="edit_product"),
    path('delete-product/<int:product_id>/', DeleteProductView.as_view(), name="delete_product" ),
    
    path('comments/<int:product_id>/', CommentsProduct.as_view(), name='comentarios_producto'),
    path('new-comment/', NewCommentView.as_view(), name='nuevo_comentario'),
    path('edit-comment/<int:comment_id>/', EditCommentView.as_view(), name='editar_comentario'),
    path('delete-comment/<int:comment_id>/', DeleteCommnetView.as_view(), name='eliminar_comentario'),
]