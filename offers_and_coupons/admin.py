from django.contrib import admin

from .models import Offers, Coupon, UserCoupon
# Register your models here.

@admin.register(Offers)
class OffersAdmin(admin.ModelAdmin):
    list_display = ("id", "title")

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "description")

@admin.register(UserCoupon)
class UserCouponnAdmin(admin.ModelAdmin):
    list_display = ("id", "coupon")