
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from .models import Offers, Coupon

from products.models import Products
from products.serializer import SerializerProducts

# Serializadore para crear una nueva oferta
class NewOffertSerializer(serializers.ModelSerializer):
    # Campo para obtener el producto
    product = serializers.PrimaryKeyRelatedField(
        queryset=Products.objects.all(),
        write_only=True
    )
    # Campo de solo lectura para devolver los datos del producto
    product_detail = SerializerProducts(source='product', read_only=True)

    # Indicamos modelo y campo a utilizar
    class Meta:
        model = Offers
        fields = ['product', 'product_detail', 'title', 'description', 'percentage', 'start_date', 'end_date']
    
    # Validamos la informacion resiva don la peticion
    def validate(self, data):
        product = data.get("product")  # Ya es una instancia de Products
        user = self.context['request'].user

        if product.producer != user:
            raise serializers.ValidationError({
                "product": "El producto no existe o no tienes permisos en este."
            })

        title = data.get("title")
        if not title:
            raise serializers.ValidationError({"title": "El titulo es obligatorio"})

        description = data.get("description")
        if not description:
            raise serializers.ValidationError({"description": "La descripcion es obligatorio"})

        percentage = data.get("percentage")
        if percentage < 1 or percentage > 100:
            raise serializers.ValidationError({
                "percentage": "El porcentaje de descuento debe estar entre 1 y 100."
            })

        if percentage.as_tuple().exponent < -2:
            raise serializers.ValidationError({
                "percentage": "El porcentaje solo puede tener hasta dos decimales."
            })

        start_date = data.get('start_date', timezone.now())
        end_date = data.get('end_date')

        if start_date < timezone.now():
            raise serializers.ValidationError({
                "date": "La fecha de inicio no puede ser menor a la fecha actual."
            })

        if end_date and end_date <= start_date:
            raise serializers.ValidationError({
                "date": "La fecha de fin no puede ser menor o igual que la fecha de inicio."
            })

        return data

    # Funcion que permite crear el objeto 
    def create(self, validated_data):
        request = self.context['request']
        validated_data['seller'] = request.user
        
        offer_instance = Offers.objects.create(**validated_data)
        
        return offer_instance


# Serializador para crear un nuevo cupon
class NewCouponSerializer(serializers.ModelSerializer):
    # Campo para obtener el producto
    product = serializers.PrimaryKeyRelatedField(
        queryset=Products.objects.all(),
        write_only=True
    )
    # Campopara obtener a el creador del producto y verificar que sea el usuario logeado
    
    seller = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Coupon
        fields = ['id', 'product', 'description', 'percentage',
                  'min_purchase_amount', 'start_date', 'end_date', 'seller']
 
    # Funcion para validar la informacion
    def validate(self, data):

        percentage = data.get("percentage")
        if percentage < 1 or percentage > 100:
            raise serializers.ValidationError({
                "percentage": "El porcentaje de descuento debe estar entre 1 y 100."
            })

        if percentage.as_tuple().exponent < -2:
            raise serializers.ValidationError({
                "percentage": "El porcentaje solo puede tener hasta dos decimales."
            })

        start_date = data.get('start_date', timezone.now())
        end_date = data.get('end_date')

        if start_date < timezone.now():
            raise serializers.ValidationError({
                "date": "La fecha de inicio no puede ser menor a la fecha actual."
            })

        if end_date and end_date <= start_date:
            raise serializers.ValidationError({
                "date": "La fecha de fin no puede ser menor o igual que la fecha de inicio."
            })

        return data

    # Funciojn para crear el objeto
    def create(self, validated_data):
        request = self.context['request']
        validated_data['seller'] = request.user
        
        coupon_instance = Coupon.objects.create(**validated_data)
        
        return coupon_instance