from django.db import models

# Create your models here.

class Invoice(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='inoices')
    date_created = models.DateTimeField(auto_now_add=True)
    METHOD_CHOICES = [
        ('tarjeta_debito', 'Tarjeta de Débito'),
        ('efectivo', 'Efectivo')
    ]
    method = models.CharField(max_length=50, choices=METHOD_CHOICES, default='tarjeta_debito')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    confirmed_buyer = models.BooleanField(default=False)
    confirmed_seller = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Invoice #{self.id} - {self.user.username}'
    

class DetailInvoice(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey('products.Products', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.quantity} x {self.product.name} on Invoice #{self.invoice.id}'
    