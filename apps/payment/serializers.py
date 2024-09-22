from rest_framework import serializers
from order.models import Order


class PaymentCreateSerializer(serializers.Serializer):
    card_number = serializers.CharField()
    expiry_month = serializers.CharField()
    expiry_year = serializers.CharField()
    cvc = serializers.CharField()


class PaymentConfirmSerializer(serializers.Serializer):
    client_secret = serializers.CharField()


class PaymentStatusSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = ['status']


class PaymentSuccessSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)
