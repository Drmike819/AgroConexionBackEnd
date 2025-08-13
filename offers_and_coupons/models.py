from django.db import models

from django.utils import timezone
from datetime import timedelta

from users.models import CustomUser
from products.models import Products
# Create your models here.

#
class Offers(models.Model):
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="offers")
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'

    def is_active(self):
        now = timezone.now()
        return self.active and self.start_date <= now <= self.end_date

    def __str__(self):
        return f"{self.title} - {self.percentage}%"