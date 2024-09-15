import random
import re
import string
import uuid
from secrets import token_urlsafe
from typing import Any, Union

import requests
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import SimpleLazyObject
from django.utils.translation import gettext as _
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from core.settings import config

from user.models import Group
from user.models import User, Policy

redis_conn = get_redis_connection("default")


def generate_token():
    return str(uuid.uuid4())


def generate_otp(
        phone_number_or_email: str,
        expire_in: int = 120,
        check_if_exists: bool = True
) -> tuple[str, str]:
    otp_code = "".join(random.choices(string.digits, k=6))
    secret_token = token_urlsafe()
    redis_conn.set(f"{phone_number_or_email}:otp_secret", secret_token, ex=expire_in)
    otp_hash = make_password(f"{secret_token}:{otp_code}")
    key = f"{phone_number_or_email}:otp"
    if check_if_exists:
        if redis_conn.exists(key):
            ttl = redis_conn.ttl(key)
            raise ValidationError(_("You have a valid OTP code. Please try again in {ttl} seconds.").format(ttl=ttl),
                                  400)
    else:
        redis_conn.delete(key)
    redis_conn.set(key, otp_hash, ex=expire_in)
    return otp_code, secret_token


def check_otp(phone_number: str, otp_code: str, otp_secret: str) -> None:
    stored_hash: bytes = redis_conn.get(f"{phone_number}:otp")
    if not stored_hash or not check_password(f"{otp_secret}:{otp_code}", stored_hash.decode()):
        raise ValidationError(_("Invalid OTP code."), 400)


def response(
        data: Any = None,
        message: str = "Success",
        code: int = status.HTTP_200_OK,
        headers: dict = None,
) -> Response:
    """
    With this function we prepare our own response for the frontend.
    We always use this function when returning a response to the frontend.

    We can call this function like this:
    response(data={'foo': 'bar'}, code=200, message="Workflow run successfully")

    """
    success = True if 100 < code < 399 else False
    return Response(
        {"success": success, "code": code, "message": message, "data": data},
        headers=headers,
        status=200,
    )


def send_email(email, otp_code):
    subject = 'Welcome to Our Service!'
    message = render_to_string('emails/email_template.html', {
        'email': email,
        'otp_code': otp_code
    })

    email = EmailMessage(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email]
    )
    email.content_subtype = 'html'
    try:
        email.send(fail_silently=False)
        return 200
    except Exception as e:
        return 400


class CustomPasswordValidator:
    def __init__(self, min_length=5, require_digit=True, require_special_character=False):
        self.min_length = min_length
        self.require_digit = require_digit
        self.require_special_character = require_special_character

    def validate(self, password: str, confirm_password: str = None):
        if not password:
            raise ValidationError(_("Password is required"), code=400)

        if len(password) < self.min_length:
            raise ValidationError(
                _("Password must be at least {min_length} characters long.").format(min_length=self.min_length),
                code=400
            )

        if self.require_digit and not any(char.isdigit() for char in password):
            raise ValidationError(_("Password must contain at least one digit."), code=400)

        if self.require_special_character and not any(not char.isalnum() for char in password):
            raise ValidationError(_("Password must contain at least one special character."), code=400)

        if password.lower().startswith("12345"):
            raise ValidationError(_("Your password can be an easy target for hackers, use a complex password"),
                                  code=400)

        if password != confirm_password:
            raise ValidationError(_("Passwords do not match"), code=400)

        return password

    def is_valid(self, password: str, confirm_password: str = None) -> bool:
        if len(password) < self.min_length:
            return False

        if self.require_digit and not any(char.isdigit() for char in password):
            return False

        if self.require_special_character and not any(char.isalnum() for char in password):
            return False

        if password.lower().startswith("12345"):
            return False

        if confirm_password:
            if password != confirm_password:
                return False
        return True


def add_permissions(obj: Union[User, Group, Policy], permissions: list[str]):
    def get_perm(perm: str) -> list:
        app_label, codename = perm.split('.')
        try:
            model = codename.split('_')[1]
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            permission, _ = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
            )
        except (IndexError, ContentType.DoesNotExist):
            permission, _ = Permission.objects.get_or_create(
                codename=codename
            )
        return permission

    if isinstance(obj, User):
        obj.user_permissions.clear()
        obj.user_permissions.add(*map(get_perm, permissions))
    elif isinstance(obj, Group) or isinstance(obj, Policy):
        obj.permissions.clear()
        obj.permissions.add(*map(get_perm, permissions))
