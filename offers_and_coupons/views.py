from .serializer import NewOffertSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

#
class NewOffertView(APIView):
    # Solo los usuarios con token JWT pueden acceder
    authentication_classes = [JWTAuthentication]
    # Solo usuarios autenticados pueden acceder
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = NewOffertSerializer(data=request.data, context={'request':request})
        
        serializer.is_valid(raise_exception=True)
        
        offer_instance = serializer.save()
        
        return Response({'message': f'La oferta creada al producto {offer_instance.product.name} ha sido creada con exito'}, status=status.HTTP_201_CREATED)