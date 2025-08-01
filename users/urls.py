from django.urls import path
from .views import RegisterView, LoginView, LogoutView, RegisterGroupView, UserUpdateView
# url de la aplicacion (users)
urlpatterns = [
    # URLS
    path('register/', RegisterView.as_view(), name='register'),
    path('group/register/', RegisterGroupView.as_view(), name='register_group'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("update/", UserUpdateView.as_view(), name="update-user"),
]