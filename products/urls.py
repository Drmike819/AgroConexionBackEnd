from django.urls import path
from .views import CategoriesView, ProducsCategoriesView, ProducstView, DetailProductView, FormProductosView, EditProductView, DeleteProductView, UserProductsView
# url de la aplicacion (users)
urlpatterns = [
    # URLS
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('categories/producs/', ProducsCategoriesView.as_view(), name='products_categories'),
    path('list-products/', ProducstView.as_view(), name='Products'),
    path('my-products/', UserProductsView.as_view(), name="mis_productos" ),
    path('product/<int:product_id>/', DetailProductView.as_view(), name='Detail_product'),
    path('form/new-product/', FormProductosView.as_view(), name='formulario_producto'),
    path('edit-product/<int:product_id>/', EditProductView.as_view(), name="edit_product"),
    path('delete-product/<int:product_id>/', DeleteProductView.as_view(), name="delete_product" )
]