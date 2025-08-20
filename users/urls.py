from django.urls import path
from .views import (
    CurrentUserView, RegisterView, LogoutView, 
    RegisterGroupView, UserUpdateView, 
    VerifyAccountView, LoginView, LoginViewStep2, ToggleTwoFactorView,
    RequestPasswordChangeView, ConfirmPasswordChangeView, RequestPasswordResetView, ConfirmPasswordResetView
)
# url de la aplicacion (users)
urlpatterns = [
    # URLS
    path('my-info/', CurrentUserView.as_view(), name='current-user'),
    path('register/', RegisterView.as_view(), name='register'),
    path('group/register/', RegisterGroupView.as_view(), name='register_group'),
    
    path('verify-account/', VerifyAccountView.as_view(), name='verify-account'),
    
    path('login/', LoginView.as_view(), name='login'),
    path('login/step2/', LoginViewStep2.as_view(), name='login-step2'),
    path('toggle-2fa/', ToggleTwoFactorView.as_view(), name='toggle-2fa'),
    
    path('logout/', LogoutView.as_view(), name='logout'),
    
    path('update/', UserUpdateView.as_view(), name="update-user"),
    
    path('change-password/request/', RequestPasswordChangeView.as_view(), name='request-password-change'),
    path('change-password/confirm/', ConfirmPasswordChangeView.as_view(), name='confirm-password-change'),
    
    path('password-reset/request/', RequestPasswordResetView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', ConfirmPasswordResetView.as_view(), name='password-reset-confirm'),

]