from django.urls import path
from .views import RegisterView, LoginView
# url de la aplicacion (users)
urlpatterns = [
    # URLS
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
]