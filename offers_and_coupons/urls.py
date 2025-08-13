from django.urls import path
from .views import (
    NewOffertView,
)
# url de la aplicacion (users)
urlpatterns = [
    # URLS
    path('new-offert/', NewOffertView.as_view(), name='new_offert'), 
]
