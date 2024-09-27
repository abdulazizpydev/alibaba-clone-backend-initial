from rest_framework import serializers
from .models import Wishlist, Product
from product.serializers import ProductSerializer


class WishlistSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(write_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'created_by', 'product', 'created_at', 'product_id']
        read_only_fields = ['id', 'created_by', 'created_at', 'product']

    def validate_product_id(self, value):
        """Ensure the product exists."""
        try:
            product = Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        return value

    def create(self, validated_data):
        """Override the create method to handle wishlist creation."""
        user = self.context['request'].user
        product_id = validated_data.pop('product_id')
        product = Product.objects.get(id=product_id)

        if Wishlist.objects.filter(created_by=user, product=product).exists():
            raise serializers.ValidationError({"detail": "Product is already in the wishlist."})

        # Create a new wishlist item
        wishlist_item = Wishlist.objects.create(created_by=user, product=product)
        return wishlist_item
