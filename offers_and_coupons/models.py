from django.db import models

from django.utils import timezone
from datetime import timedelta

from users.models import CustomUser
from products.models import Products
import string
from django.utils.crypto import get_random_string
# Create your models here.

# Modelo en donde el usuario vendedor agregara ofertas a susu productos
class Offers(models.Model):
    # Vendedor y creador de la oferta
    seller = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="offers")
    # Producto a el cual se le asignara la oferta
    product = models.ForeignKey(Products, on_delete=models.PROTECT,  related_name="offers")
    # Ttitulo de la oferta
    title = models.CharField(max_length=255)
    # Descripcion de la oferta
    description = models.TextField(blank=True)
    # Porcentaje de descuento de la oferta
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    # Fecha de incio
    start_date = models.DateTimeField(default=timezone.now)
    # Fecha de finalizacion
    end_date = models.DateTimeField(default=timezone.now)
    # Campo que indica si la oferta esta activa o no
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'

    # Funcion que indica si la oferta esta activa o no
    def is_active(self):
        now = timezone.now()
        return self.active and self.start_date <= now <= self.end_date

    # Funcion que retorna un mensaje
    def __str__(self):
        return f"{self.title} - {self.percentage}%"
    

# Modelo en donde el usuario podra agregar cupones y asignarlos a los compradores siempre y cuando cumplan con la codicion establecida
class Coupon(models.Model):
    # Creador del cupon
    seller = models.ForeignKey(CustomUser, on_delete=models.PROTECT,  related_name="coupons")
    # Producto al cual esta asocido el cupon
    product = models.ForeignKey(Products, on_delete=models.PROTECT, related_name="coupons")
    # Descripcion del cupon
    description = models.TextField(blank=True)
    # Porcentaje de descuento
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    # Minimo valor que debe comprar el usuario
    min_purchase_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Monto mínimo que el comprador debe gastar en este producto/vendedor"
    )
    # Indicador de fechas
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    # Indicador de estado del cupon
    active = models.BooleanField(default=True)
    code = models.CharField(max_length=6, editable=False, unique=True, null=True, blank=True)

    
    def save(self, *args, **kwargs):
        # Solo generamos el código si no existe
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        characters = string.ascii_uppercase + string.digits
        code = get_random_string(length=6, allowed_chars=characters)

        # Validamos que no exista en la BD
        while Coupon.objects.filter(code=code).exists():
            code = get_random_string(length=6, allowed_chars=characters)
        return code

    # Funcion que indica si el cuypon esta activo o no
    def is_active(self):
        now = timezone.now()
        return self.active and self.start_date <= now <= self.end_date
    # Funcion que retorna un mensaje
    def __str__(self):
        return f"{self.percentage}% ({'Activo' if self.active else 'Inactivo'})"


# Modelo en donde uniremos los cupones a el usuario comprador
class UserCoupon(models.Model):
    # Usuario comprador al cual se asociara el cupon
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT,  related_name="user_coupons")
    # Cupon asociado
    coupon = models.ForeignKey(Coupon,  on_delete=models.PROTECT, related_name="user_coupons")
    # Verificamos si el cupon se uso o no
    used = models.BooleanField(default=False)
    # Fecha en la cual se le asigno el cupon al usuario
    assigned_at = models.DateTimeField(auto_now_add=True)
    # Funcion que devuelve un mensaje
    def __str__(self):
        return f"Coupon {self.coupon.code} para {self.user.username} ({'Usado' if self.used else 'Disponible'})"
