from django.urls import path
from .views import RegisterView, LoginView, FavoritesView, FavoriteDeleteView
# url de la aplicacion (users)
urlpatterns = [
    # URLS
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('favorites/', FavoritesView.as_view(), name='MisFavorites'),
    path('favorites/<int:product_id>/', FavoriteDeleteView.as_view(), name='favorites-delete'),
]