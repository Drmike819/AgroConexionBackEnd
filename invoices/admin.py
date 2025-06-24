from django.contrib import admin
from .models import Invoice, DetailInvoice
# Register your models here.

admin.site.register(Invoice)
admin.site.register(DetailInvoice)