from django.urls import path
from .views import RegisterView, LoginView, LogoutView
# url de la aplicacion (users)
urlpatterns = [
    # URLS
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]