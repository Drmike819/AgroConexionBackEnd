
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from .models import Offers

from products.models import Products
from products.serializer import SerializerProducts
#
class NewOffertSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Products.objects.all(),
        write_only=True
    )
    # Campo de solo lectura para devolver los datos del producto
    product_detail = SerializerProducts(source='product', read_only=True)
    
    class Meta:
        model = Offers
        fields = ['product', 'product_detail', 'title', 'description', 'percentage', 'start_date', 'end_date']
    
    def validate(self, data):
        product = data.get("product")  # Ya es una instancia de Products
        user = self.context['request'].user

        if product.producer != user:
            raise serializers.ValidationError({
                "product": "El producto no existe o no tienes permisos en este."
            })

        title = data.get("title")
        if not title:
            raise serializers.ValidationError({"error": "El titulo es obligatorio"})

        description = data.get("description")
        if not description:
            raise serializers.ValidationError({"error": "La descripcion es obligatorio"})

        percentage = data.get("percentage")
        if percentage < 1 or percentage > 100:
            raise serializers.ValidationError({
                "error": "El porcentaje de descuento debe estar entre 1 y 100."
            })

        if percentage.as_tuple().exponent < -2:
            raise serializers.ValidationError({
                "error": "El porcentaje solo puede tener hasta dos decimales."
            })

        start_date = data.get('start_date', timezone.now())
        end_date = data.get('end_date')

        if start_date < timezone.now():
            raise serializers.ValidationError({
                "error": "La fecha de inicio no puede ser menor a la fecha actual."
            })

        if end_date and end_date < start_date:
            raise serializers.ValidationError({
                "error": "La fecha de fin no puede ser menor que la fecha de inicio."
            })

        return data

        
    def create(self, validate_data):
        request = self.context['request']
        validate_data['seller'] = request.user
        
        offer_instance = Offers.objects.create(**validate_data)
        
        return offer_instance