from rest_framework import serializers
from .models import Coupon
from django.utils import timezone


class CouponListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'created_by', 'code', 'active', 'discount_type', 'discount_value', 'valid_from',
                  'valid_until']


class CouponCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'created_by', 'code', 'discount_type', 'discount_value', 'valid_from', 'valid_until', 'active',
                  'max_uses']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None

        coupon = Coupon.objects.create(created_by=user, **validated_data)
        return coupon

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CouponSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(write_only=True)
    order_id = serializers.UUIDField(write_only=True)

    def validate_coupon_code(self, value):
        user = self.context['request'].user
        try:
            coupon = Coupon.objects.get(code=value, active=True)
            now = timezone.now()

            if coupon.valid_from > now:
                raise serializers.ValidationError('The coupon code is not yet valid.')
            if coupon.valid_until < now:
                raise serializers.ValidationError('The coupon code has expired.')
            if coupon.used_count >= coupon.max_uses:
                raise serializers.ValidationError('The coupon code has been used the maximum number of times.')
            if coupon.users.filter(id=user.id).exists():  # More efficient check
                raise serializers.ValidationError('You have already used this coupon.')

            return coupon
        except Coupon.DoesNotExist:
            raise serializers.ValidationError('Coupon does not exist.')
