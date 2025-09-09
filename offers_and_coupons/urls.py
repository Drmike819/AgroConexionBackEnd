from django.urls import path
from .views import (
    NewOfferView, DesactiveOffert,
    NewCoupontView, DesactiveCoupon 
)
# url de la aplicacion (users)
urlpatterns = [
    # URLS
    path('new-offert/', NewOfferView.as_view(), name='new_offert'), 
    path('offers/<int:offer_id>/active/', DesactiveOffert.as_view(), name='desactive_offer'),
    
    path('new-coupon/', NewCoupontView.as_view(), name='new_coupon'),
    path('coupon/<int:coupon_id>/active/', DesactiveCoupon.as_view(), name='desactive_coupon'),
    
]
