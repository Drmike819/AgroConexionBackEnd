from django.urls import path
from .views import CategoriesView, ProducstView, DetailProductView, FormProductosView
# url de la aplicacion (users)
urlpatterns = [
    # URLS
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('list-products/', ProducstView.as_view(), name='Products'),
    path('product/<int:product_id>/', DetailProductView.as_view(), name='Detail_product'),
    path('form/new-product/', FormProductosView.as_view(), name='formulario_producto'),
]