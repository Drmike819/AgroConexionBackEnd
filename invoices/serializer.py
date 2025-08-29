from rest_framework import serializers
from .models import Invoice, DetailInvoice
from products.models import Products
from offers_and_coupons.models import Offers, Coupon, UserCoupon
from offers_and_coupons.serializer import OfferSerializer, CouponUseSerializer, CouponSerializer
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
# Serializador para verificar la información de cada producto solicitado en una factura
class DetailProductSerializer(serializers.Serializer):

    # ID del producto a comprar
    product_id = serializers.IntegerField()
    # Cantidad solicitada del producto
    quantity = serializers.IntegerField(min_value=1)
    # Codigo del cupon
    coupon = CouponUseSerializer(required=False)
    # Validación personalizada para verificar existencia del producto y disponibilidad de stock
    def validate(self, data):
        try:
            # Buscar el producto por su ID
            product = Products.objects.get(id=data['product_id'])
        except Products.DoesNotExist:
            # Lanzar error si el producto no existe
            raise serializers.ValidationError('El producto no fue encontrado.')

        # Verificar que la cantidad solicitada no supere el stock disponible
        if product.stock < data['quantity']:
            raise serializers.ValidationError(
                f'La cantidad solicitada ({data["quantity"]}) es mayor al stock disponible '
                f'del producto "{product.name}". Cantidad disponible: {product.stock}.'
            )

        # Incluir el producto en los datos validados para uso posterior
        data['product'] = product
        return data


# Serializador para crear una nueva factura con sus detalles (productos comprados)
class InvoiceCreateSerializer(serializers.Serializer):
    
    # Campo para seleccionar el método de pago
    method = serializers.ChoiceField(choices=Invoice.METHOD_CHOICES)
    
    # Lista de productos con su cantidad e instancia del producto validado
    items = DetailProductSerializer(many=True)
    
    def validate(self, data):
        items = data.get('items', [])
        if not items:
            raise serializers.ValidationError('No se proporcionaron productos.')
        return data
    
    @transaction.atomic
    # Función para crear una factura y sus detalles
    def create(self, validated_data):
        # Obtenemso el metodo de pago, el usuario y los productos 
        user = self.context['request'].user
        method = validated_data['method']
        items = validated_data['items']

        # Creamos una factura con datos parciales
        invoice = Invoice.objects.create(user=user, method=method, total=Decimal('0.00'))
        # Indicamos que el total es cero
        total = Decimal('0.00')
        # Obtenemos la hora exacta
        now = timezone.now()

        # Recorremso los productos
        for item in items:
            # Obtenemos el producto, la cantidad a cxomprar y el precio del producto
            product = item['product']
            quantity = item['quantity']
            unit_price = product.price
            
            # Inicializamos el subtotal con el precio base
            subtotal = unit_price * quantity
            
            # Variables para descuentos aplicados
            applied_offer = None
            applied_coupon = None
            user_coupon_instance = None

            # Obtenemos la oferta del producto si existye y si esta activa
            offer = Offers.objects.filter(
                product=product, active=True,
                start_date__lte=now, end_date__gte=now
            ).first()
            # Si hay oferta
            if offer:
                # Obtenemos el descuento
                discount_percentage = offer.percentage
                # Aplicamos el descuento
                subtotal *= (1 - discount_percentage / 100)
                # Indicamos que la oferta fue aplicada
                applied_offer = offer

            # Obtenemos el cupon de la solicitud
            coupon_payload = item.get('coupon')
            if coupon_payload and coupon_payload.get('code'):
                # Si hay cupon obtenemso el codigo del mismo
                code = coupon_payload['code']
                # Verificamos que exista el cupony que este este activo
                try:
                    coupon = Coupon.objects.get(
                        code=code,
                        product=product,
                        active=True,
                        start_date__lte=now,
                        end_date__gte=now
                    )
                except Coupon.DoesNotExist:
                    raise serializers.ValidationError(f"El cupón {code} no es válido para este producto o está inactivo/expirado.")
                
                # Verificar si el usuario tiene el cupón y no lo ha usado
                user_coupon_instance = UserCoupon.objects.filter(
                    user=user, coupon=coupon, used=False
                ).first()

                if user_coupon_instance is None:
                    raise serializers.ValidationError(f"El cupón {code} no está asignado a tu usuario o ya fue utilizado.")

                # Aplicar descuento del cupón sobre el subtotal que ya fue modificado por la oferta
                discount_percentage = coupon.percentage
                subtotal *= (1 - discount_percentage / 100) # Aplica descuento directamente
                applied_coupon = coupon
                
                # 3) Marcar user coupon como usado
                user_coupon_instance.used = True
                user_coupon_instance.save()

            # Asegurarse de que el subtotal no sea negativo
            if subtotal < 0:
                subtotal = Decimal('0.00')

            # Crear el detalle de la factura
            DetailInvoice.objects.create(
                seller=product.producer,
                invoice=invoice,
                product=product,
                quantity=quantity,
                unit_price=unit_price, # El precio unitario siempre es el base
                subtotal=subtotal, # El subtotal es el precio con descuentos aplicados
                offer=applied_offer,
                coupon=applied_coupon
            )

            # Actualizar stock del producto
            product.stock -= quantity
            product.save()

            # Sumar al total de la factura
            total += subtotal
            
        # Actualizar el total de la factura
        invoice.total = total
        invoice.save()
        return invoice


# Serializador para obtener los detalles de las factura
class DetailInvoiceSerializer(serializers.ModelSerializer):
    # Creamos un campo nuevo en donde obtendremos el nombre del producto para no obtener toda la informacion del producto
    product_name = serializers.CharField(source='product.name')
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    offer = OfferSerializer(read_only=True)
    coupon = CouponSerializer(read_only = True)
    class Meta:
        # Indicamos le modelo a utilizar
        model = DetailInvoice
        # Indicamos los campos que obtenedremos en el JSON
        fields = ['product_name', 'seller_name', 'quantity', 'unit_price', 'subtotal', 'offer', "coupon"]


# Serializador para poder obtener las facturas
class InvoiceSerializer(serializers.ModelSerializer):
    # Campo que representa los detalles de la factura de una factura
    details = DetailInvoiceSerializer(many=True, read_only=True)
    # Muestra a el usuario como string no como un id (methodo __str__)
    user = serializers.StringRelatedField()

    class Meta:
        # Indicamos el modelo que utilizaremos
        model = Invoice
        # Campos que obtendremos en el JSON
        fields = [
                'id', 'user', 'date_created', 'method', 'total',
                'details',
            ]