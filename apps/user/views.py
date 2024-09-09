from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from django_redis import get_redis_connection

from share.utils import send_email, generate_otp

from .serializers import *
from .models import User

redis_conn = get_redis_connection("default")


class SignUpView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpRequestSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        phone_number = serializer.validated_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number, is_verified=True).exists():
            return Response({"detail": _("User with this phone number already exists!")},
                            status=status.HTTP_409_CONFLICT)
        if User.objects.filter(email=email, is_verified=True).exists():
            return Response({"detail": _("User with this email already exists!")},
                            status=status.HTTP_409_CONFLICT)

        user = User.objects.filter(phone_number=phone_number, email=email, is_verified=False).first()
        if not user:
            serializer.save()
        else:
            user.first_name = serializer.validated_data.get('first_name')
            user.last_name = serializer.validated_data.get('last_name')
            user.set_password(serializer.validated_data.get('password'))
            user.save()

        if redis_conn.exists(f"{phone_number}:otp_secret"):
            otp_secret = redis_conn.get(f"{phone_number}:otp_secret").decode()
            return Response({
                "phone_number": phone_number,
                "otp_secret": otp_secret,
            }, status=status.HTTP_201_CREATED)

        otp_code, otp_secret = generate_otp(
            phone_number_or_email=phone_number,
            expire_in=2 * 60,
            check_if_exists=False
        )
        send_email(email, otp_code)
        # send_email.delay(email, otp_code)
        return Response({
            "phone_number": phone_number,
            "otp_secret": otp_secret
        }, status=status.HTTP_201_CREATED)
