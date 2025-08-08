from django.urls import path
from .views import FavoritesView, FavoriteDeleteView, CartUserView, DeleteProductCartUserView 
# url de la aplicacion (users)
urlpatterns = [
    # URLS
    path('favorites/', FavoritesView.as_view(), name='MisFavorites'),
    path('favorites/<int:product_id>/', FavoriteDeleteView.as_view(), name='favorites-delete'),
    path('my-cart/', CartUserView.as_view(), name='add-to-cart'),
    path('delete-product/<int:product_id>/', DeleteProductCartUserView.as_view(), name='remove-product-cart'),
]
