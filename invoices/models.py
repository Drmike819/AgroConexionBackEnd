from django.db import models

# Create your models here.

# Creacion del modelo de la factura
class Invoice(models.Model):
    # Usuario comprador ligado a la factura
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='invoices')
    # Fecha de creacion de la factura
    date_created = models.DateTimeField(auto_now_add=True)
    # Metodos de pago que tendra la factura
    METHOD_CHOICES = [
        ('tarjeta_debito', 'Tarjeta de Débito'),
        ('efectivo', 'Efectivo')
    ]
    # Campo de factura
    method = models.CharField(max_length=50, choices=METHOD_CHOICES, default='tarjeta_debito')
    # Total de factura
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Mensaje que se vera en el admin
    def __str__(self):
        return f'Invoice #{self.id} - {self.user.username}'


# Modelo detalle factura
class DetailInvoice(models.Model):
    # Campo que liga a la factura
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='details')
    # Campo que indica el producto a comprar
    product = models.ForeignKey('products.Products', on_delete=models.PROTECT)
    # Campo donde indicamos el vendedor del producto
    seller = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='invoices_seller', default=1)
    # Cantidad que deseamos comprar
    quantity = models.PositiveIntegerField()
    # Obtenemos el precio del producto
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Calculamos el precio dependiendo de la catidad a comprar y el precio del producto
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    # Mensaje que se vera en el admin
    def __str__(self):
        return f'{self.quantity} x {getattr(self.product, "name", "Producto")} en factura #{self.invoice_id}'

    