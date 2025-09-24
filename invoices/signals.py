from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Invoice, DetailInvoice
from offers_and_coupons.models import Coupon, UserCoupon
from notifications.utils import send_notification
from django.utils import timezone

@receiver(post_save, sender=DetailInvoice)
def check_and_assign_coupon_from_detail(sender, instance, created, **kwargs):
    if not created:
        return

    # 2. Obtener la información principal
    invoice = instance.invoice
    user = invoice.user
    product = instance.product
    subtotal = instance.subtotal

    # 3. Buscar cupones asociados al producto
    coupons_disponibles = Coupon.objects.filter(product=product)

    # 4. Iterar sobre los cupones encontrados y aplicar las validaciones
    for coupon in coupons_disponibles:

        # 4a. Verificar si el cupón está activo (usando tu método is_active)
        if coupon.is_active():

            # 4b. Verificar el monto mínimo de compra
            if subtotal >= coupon.min_purchase_amount:

                # 4c. Verificar si el usuario ya tiene el cupón de ese vendedor
                seller = coupon.seller
                user_has_coupon = UserCoupon.objects.filter(
                    user=user,
                    coupon=coupon,  # mucho más claro que coupon__id
                    used=False,
                    coupon__end_date__gte=timezone.now()
                ).exists()

                if not UserCoupon.has_valid_coupon(user, coupon):
                    
                    # 5. Crear la instancia de UserCoupon
                    cupon_user = UserCoupon.objects.create(
                        user=user,
                        coupon=coupon
                    )
                    # Obtenemos la primera imagen del producto
                    first_image = product.images.first()
                    # Obtenemos la url de esa imagen
                    image_url = first_image.image.url if first_image else None
                    
                    notificacion = send_notification(
                        # Usuario al cual se le enviare la notificacion
                        user=user,
                        # Tiopo de notificacion
                        type='custom',
                        # Titulo
                        title='¡Obtubiste un Nuevo Cupon!',
                        # Mensaje
                        message=f"Haz Otenido un cupon para el producto {product.name}",
                        # Url de la imagen
                        image=image_url,
                        # Informacion que puede variar a eleccion
                        data={
                        }
                    )

                    print(notificacion)
                    print(f"Se asigno el cupon al usuario {user.username}', para un descuento de {cupon_user.coupon.percentage} para el producto {cupon_user.coupon.product.name}")
                else:
                    print(f"El usuario '{user.username}' YA tiene este cupón. No se asignará de nuevo.")