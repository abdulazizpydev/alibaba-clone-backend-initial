from rest_framework import serializers
from .models import Order, OrderItem
from product.serializers import ProductSerializer
from cart.models import Cart
from .countries import Countries
from share.enums import PaymentProvider

from core import settings


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'status',
            'payment_method',
            'amount',
            'order_items',
            'country_region',
            'city',
            'state_province_region',
            'postal_zip_code',
            'telephone_number',
            'address_line_1',
            'address_line_2',
            'shipping_name',
            'shipping_time',
            'shipping_price',
            'is_paid',
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    payment_method = serializers.ChoiceField(choices=PaymentProvider.choices(), required=True)
    country_region = serializers.ChoiceField(choices=Countries.choices, required=True)
    city = serializers.CharField(required=True)
    state_province_region = serializers.CharField(required=True)
    postal_zip_code = serializers.CharField(required=True)
    telephone_number = serializers.CharField(required=True)
    address_line_1 = serializers.CharField(required=True)

    class Meta:
        model = Order
        fields = [
            'payment_method',
            'country_region',
            'city',
            'state_province_region',
            'postal_zip_code',
            'telephone_number',
            'address_line_1',
            'address_line_2',
        ]

    def create(self, validated_data):
        total_price = 0
        user = self.context['request'].user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError('The cart is empty or does not exist.')

        cart_products = cart.items.all()

        if not cart_products.exists():
            raise serializers.ValidationError('The cart cannot be empty.')

        if Order.objects.filter(user=user, status='pending').exists():
            raise serializers.ValidationError('You have an unconfirmed order, please complete.')

        order = Order.objects.create(**validated_data)

        for cart_item in cart_products:
            quantity = cart_item.quantity
            price = cart_item.product.price * quantity
            total_price += price

            OrderItem.objects.create(order=order, product=cart_item.product, quantity=quantity, price=price)

        order.amount = total_price
        order.save()

        return order
