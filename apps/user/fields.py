import re

from rest_framework import serializers

from core.settings import config
from django.db import models

from user.crypto import decrypt_password, encrypt_password, initialize_cipher
from django.utils.translation import gettext_lazy as _


class EncryptedPasswordField(models.BinaryField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fernet_key = config("FERNET_KEY")
        assert fernet_key is not None
        self.cipher = initialize_cipher(fernet_key)

    def get_prep_value(self, value):
        if value is not None:
            return encrypt_password(self.cipher, value)
        return value

    def from_db_value(self, value, expression, connection):
        if value is not None:
            return decrypt_password(self.cipher, value)
        return value

    def to_python(self, value):
        if value is not None:
            return decrypt_password(self.cipher, value)
        return value


class PhoneNumberField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        self.validate_phone_number(value)
        return value

    def validate_phone_number(self, value):
        pattern = r'^\+998\d{9}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                _("Invalid phone number format. Should start with +998 and have 9 digits after.")
            )


class OtpCodeField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        self.validate_otp_code(value)
        return value

    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(_("Invalid code format. Only str digits are allowed."))
