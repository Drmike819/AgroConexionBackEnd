from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Invoice, DetailInvoice
from offers_and_coupons.models import Coupon, UserCoupon

@receiver(post_save, sender=Invoice)
def check_and_assign_coupon(sender, instance, created, **kwargs):
    if not created:
        return

    # Obtener el usuario que realizó la compra
    user = instance.user

    # Obtener todos los detalles de la factura recién creada
    detail_invoice_items = DetailInvoice.objects.filter(invoice=instance)

    # Agrupar los detalles por vendedor para verificar los cupones
    vendedores_y_productos = {}
    for detail in detail_invoice_items:
        # Asumimos que el producto tiene un campo 'seller' o que podemos obtenerlo a través de la relación.
        # En este caso, lo obtendremos del modelo Coupon.
        product = detail.product
        subtotal = detail.subtotal

        # Buscar cupones asociados a este producto y que estén activos
        cupones_disponibles = Coupon.objects.filter(product=product, active=True).filter(
            start_date__lte=instance.created_at, end_date__gte=instance.created_at
        )

        for coupon in cupones_disponibles:
            if coupon.is_active():
                # 1. Verificar si el monto comprado del producto cumple con el requisito del cupón
                if subtotal >= coupon.min_purchase_amount:

                    # 2. Verificar que el usuario no tenga ya este cupón de este mismo vendedor
                    vendedor = coupon.seller
                    
                    # Usamos exists() para una verificación más eficiente
                    user_has_coupon = UserCoupon.objects.filter(
                        user=user,
                        coupon__product=product, # Filtra por el producto asociado al cupón
                        coupon__seller=vendedor # Filtra por el vendedor del cupón
                    ).exists()

                    if not user_has_coupon:
                        # Crear la instancia de UserCoupon
                        UserCoupon.objects.create(
                            user=user,
                            coupon=coupon
                        )
                        print(f"Cupón de {coupon.percentage}% asignado a {user.username} por la compra de {product.name}.")