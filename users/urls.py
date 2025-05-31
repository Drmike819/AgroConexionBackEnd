from django.urls import path
from .views import RegisterView, LoginView, FavoritesView, FavoriteDeleteView, CartUserView, DeleteProductCartUserView
# url de la aplicacion (users)
urlpatterns = [
    # URLS
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('favorites/', FavoritesView.as_view(), name='MisFavorites'),
    path('favorites/<int:product_id>/', FavoriteDeleteView.as_view(), name='favorites-delete'),
    path('cart/', CartUserView.as_view(), name='add-to-cart'),
    path('cart/<int:product_id>/', DeleteProductCartUserView.as_view(), name='remove-from-cart'),
]