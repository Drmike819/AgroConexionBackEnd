from django.urls import path
from .views import (
    NotificatiosnView, DeleteNotificationView
)
# url de la aplicacion (users)
urlpatterns = [
    # URLS
    path('list/', NotificatiosnView.as_view(), name='notifications'),
    path('delete/<int:notification_id>/', DeleteNotificationView.as_view(), name='delete_notification'),
]