from user.models import Group
from django.utils.translation import gettext as _
from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import ValidationError

from share.utils import CustomPasswordValidator
from share.enums import UserRole, GenderChoices

from user.fields import PhoneNumberField, OtpCodeField
from user.models import User, BuyerUser, SellerUser


class SignUpRequestSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    phone_number = PhoneNumberField()
    user_trade_role = serializers.ChoiceField(
        choices=UserRole.choices(),
        write_only=True,
        required=True,
    )
    gender = serializers.ChoiceField(
        choices=GenderChoices.choices(),
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "gender",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "password",
            "confirm_password",
            "user_trade_role",
        ]

    def validate(self, attrs):
        if not (attrs.get("email") and attrs.get("phone_number")):
            raise serializers.ValidationError(_("Email and phone number required!"))

        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        validator = CustomPasswordValidator(
            min_length=5, require_digit=True, require_special_character=False
        )
        validator.validate(password, confirm_password)

        return attrs

    def create(self, validated_data):
        user_trade_role = validated_data.pop("user_trade_role")
        gender = validated_data.pop("gender")

        user = User.objects.create(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data.get("phone_number"),
            email=validated_data.get("email"),
            is_verified=validated_data.get("is_verified", False),
            gender=gender.lower()
        )
        user.set_password(validated_data["password"])
        user.is_active = False
        user.save()

        group_name = user_trade_role.lower()
        try:
            if group_name in [UserRole.BUYER.value, UserRole.SELLER.value]:
                group, is_created = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
        except Group.DoesNotExist:
            raise serializers.ValidationError(_("Invalid user role provided!"), 400)

        return user


class VerifyCodeSerializer(serializers.Serializer):
    otp_code = OtpCodeField()
    phone_number = PhoneNumberField()