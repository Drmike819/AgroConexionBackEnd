from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from .models import Offers, Coupon
from products.models import Products
from rest_framework.generics import get_object_or_404
from .serializer import NewOffertSerializer, NewCouponSerializer

# Create your views here.

# Vista para crear una nueva oferta
class NewOfferView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def verify_offer(self, request):
        product_id = request.data.get("product")
        if not product_id:
            return None

        # Traemos las ofertas relacionadas al producto y activas
        offers = Offers.objects.filter(product_id=product_id, active=True)

        # Filtramos las que realmente estén activas según la fecha
        valid_offers = [offer for offer in offers if offer.is_active()]
        return valid_offers if valid_offers else None

    def post(self, request, *args, **kwargs):
        # Validamos que el producto exista y sea del usuario
        try:
            Products.objects.get(id=request.data['product'], producer=request.user)
        except Products.DoesNotExist:
            return Response(
                {'product': 'El producto no existe o no tienes permisos para asignar una oferta a este producto'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Verificamos si ya tiene una oferta activa
        existing_offers = self.verify_offer(request)
        if existing_offers:
            return Response(
                {'error': f'El producto ya tiene una oferta activa ({existing_offers[0].percentage}% de descuento)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validamos la data con el serializador
        serializer = NewOffertSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        # Guardamos la oferta
        offer_instance = serializer.save()

        return Response(
            {'message': f'La oferta "{offer_instance.title}" para el producto {offer_instance.product.name} ha sido creada con éxito'},
            status=status.HTTP_201_CREATED
        )


# Vista ppara cambiart el estado de la oferta
class DesactiveOffert(APIView):
        # Solo los usuarios con token JWT pueden acceder
    authentication_classes = [JWTAuthentication]
    # Solo usuarios autenticados pueden acceder
    permission_classes = [IsAuthenticated]
    # Obtenemos y retornamos el id de la oferta si existe
    def get_object(self, offer_id, request):
        try:
            # Buscar oferta que pertenezca al usuario autenticado
            return Offers.objects.get(id=offer_id, seller=request.user)
        except Offers.DoesNotExist:
            return None
    # METHOD PUT       
    def put(self, request, offer_id):
        # Obtenemos la oferta en concreto
        offer =  self.get_object(offer_id, request)
        # Mnesaje de error sie no la encontramos
        if not offer :
            return Response({"error": "La oferta no existe o no tienes permisos para modificarla."}, status=status.HTTP_404_NOT_FOUND)
        active = request.data['active']
        if active is None:
            return Response({"error": "Debe indicar si quiere activar o desactivar el la oferta"}, status=status.HTTP_400_BAD_REQUEST)
        # Guardamos el estado de la oferta y la actualizamos
        offer.active = active
        offer.save()

        return Response(
            {"message": f"La oferta '{offer.title}' fue {'activada' if active else 'desactivada'} correctamente."},
            status=status.HTTP_200_OK
        )


# Vista pra crear un nuevo cupon
class NewCoupontView(APIView):
    # Solo los usuarios con token JWT pueden acceder
    authentication_classes = [JWTAuthentication]
    # Solo usuarios autenticados pueden acceder
    permission_classes = [IsAuthenticated]
    # METOD POST
    def verify_coupon(self, request):
        product_id = request.data.get("product")
        if not product_id:
            return None

        # Traemos los cupones relacionados al producto y que estén marcados como activos
        coupons = Coupon.objects.filter(product_id=product_id, active=True)

        # Filtramos los que realmente estén activos según la fecha
        valid_coupons = [coupon for coupon in coupons if coupon.is_active()]

        return valid_coupons if valid_coupons else None
    
    def post(self, request, *args, **kwargs):
        # Obtenemos y verificamose l producto de la petcion
        try:
            Products.objects.get(id=request.data['product'], producer=request.user)
        except Products.DoesNotExist:
            return Response({'product': 'El producto no existe o no tienes permisos para asignar una oferta al producto'}, status=status.HTTP_401_UNAUTHORIZED)
        
        existing_coupons = self.verify_coupon(request)
        if existing_coupons:
            return Response(
                {'error': f'El producto ya tiene un cupón activo ({existing_coupons[0].percentage}% de descuento)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Llamamos al serializador
        serializer = NewCouponSerializer(data=request.data, context={'request':request})
        # Verificamos que la informacion sea valida
        serializer.is_valid(raise_exception=True)
        # Creamos el objeto
        coupon_instance = serializer.save()
        # Mensaje de exito
        return Response({'message': f'El cupon creado para el producto {coupon_instance.product.name} ha sido creada con exito'}, status=status.HTTP_201_CREATED)


# Vistya para editar el estado de un cupon
class DesactiveCoupon(APIView):
    # Solo los usuarios con token JWT pueden acceder
    authentication_classes = [JWTAuthentication]
    # Solo usuarios autenticados pueden acceder
    permission_classes = [IsAuthenticated]
    
    # Retornamos el cupon a editar 
    def get_object(self, coupon_id, request):
        try:
            # Buscar oferta que pertenezca al usuario autenticado
            return Coupon.objects.get(id=coupon_id, seller=request.user)
        except Coupon.DoesNotExist:
            return None
    
    # METHOD POST
    def put(self, request, coupon_id):
        # Obtenemos el cupom
        coupon =  self.get_object(coupon_id, request)
        # En caso de no obtenerlo retornamos mensaje de error
        if not coupon :
            return Response({"error": "La oferta no existe o no tienes permisos para modificarla."}, status=status.HTTP_404_NOT_FOUND)
        active = request.data['active']
        if active is None:
            return Response({"error": "Debe indicar si quiere activar o desactivar el la oferta"}, status=status.HTTP_400_BAD_REQUEST)
        # Guardamos el nuevo estado
        coupon.active = active
        coupon.save()
        # Retornamos mensaje de exito
        return Response(
            {"message": f"La oferta fue {'activada' if active else 'desactivada'} correctamente."},
            status=status.HTTP_200_OK
        )