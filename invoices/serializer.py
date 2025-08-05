from rest_framework import serializers
from .models import Invoice, DetailInvoice
from products.models import Products

# Serializador para verificar la información de cada producto solicitado en una factura
class DetailProductSerializer(serializers.Serializer):

    # ID del producto a comprar
    product_id = serializers.IntegerField()
    # Cantidad solicitada del producto
    quantity = serializers.IntegerField(min_value=1)

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
    
    # Función para crear una factura y sus detalles
    def create(self, validated_data):
        # Obtenemos el usuario autenticado desde el contexto
        user = self.context['request'].user
        
        # Obtenemos el método de pago seleccionado
        method = validated_data['method']
        
        # Obtenemos la lista de productos con cantidades a comprar
        items = validated_data['items']
        
        invoice = Invoice.objects.create(
            user=user, 
            method=method,
            total=0,
        )
        total = 0
        
        # Iteramos sobre los productos para crear cada detalle de factura
        for item in items:
            # Obtenemos la instancia del producto
            product = item['product']
            
            # Obtenemos la cantidad comprada
            quantity = item['quantity']
            
            # Obtenemos el precio unitario del producto
            unit_price = product.price
            
            # Calculamos el subtotal del producto
            subtotal = unit_price * quantity

            # Creamos el detalle de factura
            DetailInvoice.objects.create(
                seller=product.producer,
                invoice=invoice,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal
            )

            # Descontamos la cantidad comprada del stock del producto
            product.stock -= quantity
            product.save()
            
            # Sumamos el subtotal al total general
            total += subtotal

        # Actualizamos el total de la factura
        invoice.total = total
        invoice.save()

        # Retornamos la factura creada
        return invoice


# Serializador para obtener los detalles de las factura
class DetailInvoiceSerializer(serializers.ModelSerializer):
    # Creamos un campo nuevo en donde obtendremos el nombre del producto para no obtener toda la informacion del producto
    product_name = serializers.CharField(source='product.name')
    seller_name = serializers.CharField(source='seller.username', read_only=True)

    class Meta:
        # Indicamos le modelo a utilizar
        model = DetailInvoice
        # Indicamos los campos que obtenedremos en el JSON
        fields = ['product_name', 'seller_name', 'quantity', 'unit_price', 'subtotal']


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