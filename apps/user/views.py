from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from django_redis import get_redis_connection
from share.permissions import GeneratePermissions, check_perm
from share.utils import send_email, generate_otp, check_otp

from .serializers import *
from .models import User
from .services import UserService

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


class VerifyView(generics.UpdateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyCodeSerializer
    http_method_names = ['patch']
    authentication_classes = []

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_code = serializer.validated_data['otp_code']
        phone_number = serializer.validated_data['phone_number']
        otp_secret = kwargs.get('otp_secret')
        check_otp(phone_number, otp_code, otp_secret)
        user = User.objects.filter(phone_number=phone_number, is_verified=False).first()
        if not user:
            return Response({"detail": _("Unverified user not found!")}, status=status.HTTP_404_NOT_FOUND)
        user.is_verified = True
        user.is_active = True
        user.save()
        redis_conn.delete(f"{phone_number}:otp")
        redis_conn.delete(f"{phone_number}:otp_secret")
        tokens = UserService.create_tokens(user)
        return Response(tokens, status=status.HTTP_200_OK)


class LoginViewSet(viewsets.ModelViewSet):
    serializer_class = LoginSerializer
    http_method_names = ['post']
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.authenticate(**serializer.validated_data)
        if isinstance(user, ValidationError):
            raise user

        tokens = UserService.create_tokens(user)
        return Response(tokens)

class UsersMeView(GeneratePermissions, generics.RetrieveAPIView, generics.UpdateAPIView):
    http_method_names = ['get', 'patch']
    # permission_classes = [check_perm('user.change_user_me')]

    def get_object(self):
        user = self.request.user

        if user.groups.filter(name="buyer").exists():
            try:
                return user.buyer_profile
            except BuyerUser.DoesNotExist:
                raise serializers.ValidationError("Buyer profile does not exist for this user.")

        if user.groups.filter(name="seller").exists():
            try:
                return user.seller_profile
            except SellerUser.DoesNotExist:
                raise serializers.ValidationError("Seller profile does not exist for this user.")

        raise serializers.ValidationError("User does not belong to either Buyer or Seller group.")

    def get_serializer_class(self):
        if self.request.user.groups.filter(name="seller").exists():
            return SellerUserSerializer
        elif self.request.user.groups.filter(name="buyer").exists():
            return BuyerUserSerializer

        return BuyerUserSerializer
