from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializer import InvoiceCreateSerializer, InvoiceSerializer, DetailInvoice
from django.db import transaction
from django.db.models import Sum

from cart.models import ShoppingCart

from .models import Invoice
# Create your views here.


# Creamos la vista para crear una nueva factura desde el carrito del usuario
class InvoiceFromCartView(APIView):
    # Indicamos la clase de untentificacion necesaria
    authentication_classes = [JWTAuthentication]
    # indicamos que la vista solo se puede acceder si esta autenticado
    permission_classes = [IsAuthenticated]

    # Metodo post
    def post(self, request):
        try:
            # Obtenemos el carrito del usuario con el usuario autenticado
            cart = ShoppingCart.objects.get(user=request.user)
            # mensaje de error si el usuario no esta autenticado
        except ShoppingCart.DoesNotExist:
            return Response({'detail': 'No tienes productos en el carrito'}, status=400)
        # Verificamos que el carrito tenga productos
        if not cart.products.exists():
            return Response({'detail': 'Tu carrito está vacío'}, status=400)

        # Convertir productos del carrito al formato esperado
        items = []
        # Recorremos el carrito y obtenemos la informacion necesaria
        for cart_item in cart.products.all():
            # Agregamos el id del producto y la catidad deseada
            items.append({
                'product_id': cart_item.product.id,
                'quantity': cart_item.quantity
            })

        # Obtenemos el metodo elegido por el usuario
        payment_method = request.data.get('method', 'efectivo')
        
        # Verifica que el metodo elegido exista
        valid_methods = [choice[0] for choice in Invoice.METHOD_CHOICES]
        if payment_method not in valid_methods:
            return Response(
                {'detail': f'Método de pago inválido. Opciones válidas: {valid_methods}'},
                status=400
            )
        
        # Agregamos la informacion a data
        data = {
            'method': payment_method,
            'items': items
        }
        
        #  Verificamos el serializador pasando la informacion y el contexto
        serializer = InvoiceCreateSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            # Esto garantiza que todo  lo andentro del codigo se ejecute de manera correcta o no se ejecute
            with transaction.atomic():
                # Creamos una factura con los datos
                invoice = serializer.save()
                # Limpiar el carrito después de generar la factura
                cart.products.all().delete()
                # Convierte la factura en un serialzador para enviarlo al cliente
                output_serializer = InvoiceSerializer(invoice, context={'request': request})
                # Enviamo la inforamcion al cliente
                return Response(output_serializer.data, status=201)
        # Mensaje de error
        return Response(serializer.errors, status=400)


# Vista qu epermite crear una factura
class InvoicesView(APIView):
    # Indicamo el metodo de autenticacion
    authentication_classes = [JWTAuthentication]
    # Solo los usuarios autenticados pueden acceder a esta vista
    permission_classes = [IsAuthenticated]
    
    # Metodo post
    def post(self, request):
        # Verificamos que el metodo de pago sea enviado
        if 'method' not in request.data:
            return Response({'detail': 'El campo "method" es obligatorio.'}, status=400)
        
        # Obtenemos el metodo elegido por el usuario
        payment_method = request.data.get('method', 'efectivo')
        valid_methods = [choice[0] for choice in Invoice.METHOD_CHOICES]
        # Verifica que el metodo elegido exista
        if payment_method not in valid_methods:
            return Response(
                {'detail': f'Método de pago inválido. Opciones válidas: {valid_methods}'},
                status=400
            )
        serializer = InvoiceCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Esto garantiza que todo  lo andentro del codigo se ejecute de manera correcta o no se ejecute
            with transaction.atomic():
                # Creamos una factura con los datos
                invoice = serializer.save()
                # Convierte la factura en un serialzador para enviarlo al cliente
                output_serializer = InvoiceSerializer(invoice, context={'request': request})
                # Enviamo la inforamcion al cliente
                return Response(output_serializer.data, status=201)
        # Mensaje de error
        return Response(serializer.errors, status=400)


# Serializador que nos permite obtener la facturas de un usuario
class InvoiceListView(ListAPIView):
    # Metodo de autenticacion
    authentication_classes = [JWTAuthentication]
    # Permiso de la vista
    permission_classes = [IsAuthenticated]
    # Obtenemos el serializador
    serializer_class = InvoiceSerializer

    # Obtenemos la factura por el id del usuario autenticado
    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user)

    # Obtenemos el contexto del usuario
    def get_serializer_context(self):
        return {'request': self.request}
    
    
# Vista  para la obtencion de una factura en espesifico   
class InvoiceDetailView(RetrieveAPIView):
    # Metodo de autenticacion
    authentication_classes = [JWTAuthentication]
    # Permiso de la vista
    permission_classes = [IsAuthenticated]
    # Inidcamos el modelo de busqueda
    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user)
    
    # Indicamos el serializador
    serializer_class = InvoiceSerializer
    # Indicamos que la busqueda de la factura debe ser el id
    lookup_field = 'id'

    # Obtenemos el contexto
    def get_serializer_context(self):
        return {'request': self.request}
    

# Vista que nos permite ver estadisticas
class UserStatsView(APIView):
    # Auteticacion requerida
    authentication_classes = [JWTAuthentication]
    # Tipo de permisos para acceder a la vista
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtenemos el usuario logeado
        user = request.user

        # Total gastado por el usuario como comprador
        total_spent = Invoice.objects.filter(user=user).aggregate(total=Sum('total'))['total'] or 0

        # Total ganado por el usuario como vendedor
        total_earned = DetailInvoice.objects.filter(seller=user).aggregate(total=Sum('subtotal'))['total'] or 0

        # Producto más vendido (por cantidad total en todas las facturas)
        most_sold = (
            DetailInvoice.objects
            .values('product__name')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')
            .first()
        )

        # Producto menos vendido (por cantidad total en todas las facturas)
        least_sold = (
            DetailInvoice.objects
            .values('product__name')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('total_quantity')
            .first()
        )

        return Response({
            'total_spent': total_spent,
            'total_earned': total_earned,
            'most_sold_product': {
                'name': most_sold['product__name'] if most_sold else None,
                'quantity': most_sold['total_quantity'] if most_sold else 0
            },
            'least_sold_product': {
                'name': least_sold['product__name'] if least_sold else None,
                'quantity': least_sold['total_quantity'] if least_sold else 0
            }
        })