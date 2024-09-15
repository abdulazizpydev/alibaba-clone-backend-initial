from rest_framework import serializers
from .models import Cart, CartItem
from product.models import Product
from product.serializers import ProductSerializer
from django.shortcuts import get_object_or_404


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(write_only=True)
    product = ProductSerializer(read_only=True)
    quantity = serializers.IntegerField(min_value=1, default=1)
    price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['product_id', 'product', 'quantity', 'price']

    def get_price(self, obj):
        return obj.product.price * obj.quantity

    def validate(self, attrs):
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity')

        # Validate product existence and stock availability
        product = get_object_or_404(Product, id=product_id)
        if product.quantity < quantity:
            raise serializers.ValidationError({'error': 'Not enough of this item in stock'})

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        user = request.user

        product_id = validated_data.get('product_id')
        quantity = validated_data.get('quantity')

        # Get or create the cart for the user
        cart, _ = Cart.objects.get_or_create(user=user)

        product = Product.objects.get(id=product_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if created:
            # If the cart item is newly created, set the initial quantity
            cart_item.quantity = quantity
        else:

            if quantity > product.quantity:
                raise serializers.ValidationError({'error': 'Not enough of this item in stock'})

            cart_item.quantity = quantity

        # Save the cart item with the updated quantity
        cart_item.save()

        # Optionally update the cart total items count if using Option 1
        cart.update_total_items()

        return cart_item


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField(source='get_total')
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total', 'total_items']

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())
