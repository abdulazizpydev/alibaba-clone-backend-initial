from uuid import UUID

import phonenumbers
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from phonenumbers import NumberParseException

from share.managers import BaseCRUDManager


class CustomUserManager(BaseUserManager, BaseCRUDManager):
    def get_active_verified_users(self):
        return self.filter(is_active=True, is_verified=True)

    def get_active_verified_user(self, user_id: UUID):
        return self.filter(user_id=user_id, is_active=True, is_verified=True)

    def reset_password(self, phone_number: str, password: str):
        user = self.get_obj(phone_number=phone_number)
        user.set_password(password)
        user.save()
        return user

    def reset_password_email(self, email: str, password: str):
        user = self.get_obj(email=email)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        if email:
            validate_email(email)
            email = self.normalize_email(email)
        if phone_number:
            try:
                parsed_number = phonenumbers.parse(phone_number)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise ValueError(_("Please enter a valid phone number."))
            except NumberParseException:
                raise ValueError(_("Please enter a valid phone number."))

        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self, email=None, phone_number=None, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        return self.create_user(email, phone_number, password, **extra_fields)
