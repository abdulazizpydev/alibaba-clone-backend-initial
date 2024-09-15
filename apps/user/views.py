from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from django_redis import get_redis_connection
from share.permissions import GeneratePermissions, check_perm
from share.utils import send_email, generate_otp, check_otp
from share.services import TokenService
from share.enums import TokenType
from django.contrib.auth.hashers import make_password
from secrets import token_urlsafe

from core import settings
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

    def get_queryset(self):
        return User.objects.all()

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

        raise serializers.ValidationError("User does not belong to either Buyer or Seller group.")


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [check_perm('user.change_user_me')]
    http_method_names = ['put']

    def put(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        tokens = UserService.create_tokens(user)
        return Response(tokens)
    


class ForgotPasswordView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        if not User.objects.filter(email=email, is_verified=True).first():
            raise ValidationError(_("No verified user found with this email!"), code=404)

        if redis_conn.exists(f"{email}:otp_secret"):
            otp_secret = redis_conn.get(f"{email}:otp_secret").decode()
            return Response({
                "email": email,
                "otp_secret": otp_secret,
            })
        otp_code, otp_secret = generate_otp(phone_number_or_email=email, expire_in=2 * 60)
        res_code = send_email(email, otp_code)
        if res_code == 200:
            return Response({
                "email": email,
                # "otp_code": otp_code,  # it's temporary for testing
                "otp_secret": otp_secret,
            })
        else:
            redis_conn.delete(f"{email}:otp")
            return Response({"detail": _("Something is wrong with sending SMS")}, status=res_code)


class ForgotPasswordVerifyView(generics.CreateAPIView):
    authentication_classes = []
    serializer_class = ForgotPasswordVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_code = serializer.validated_data['otp_code']
        email = serializer.validated_data['email']
        qs = User.objects.filter(email=email, is_verified=True)
        if not qs.exists():
            raise ValidationError(_("No verified user found with this email!"), code=404)
        otp_secret = kwargs.get('otp_secret')
        check_otp(email, otp_code, otp_secret)
        redis_conn.delete(f"{email}:otp")
        token_hash = make_password(token_urlsafe())
        redis_conn.set(token_hash, email, ex=2 * 60 * 60)
        return Response({"token": token_hash})


class ResetPasswordView(generics.UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['patch']
    authentication_classes = []

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_hash = serializer.validated_data['token']
        email: bytes = redis_conn.get(token_hash)
        if not email:
            raise ValidationError(_("Invalid token"))
        email = email.decode()
        qs = User.objects.filter(email=email, is_verified=True)
        if not qs.exists():
            raise ValidationError(_("No verified user found with this email!"), code=404)

        password = serializer.validated_data['password']
        user = User.objects.reset_password_email(email, password)
        tokens = UserService.create_tokens(user)
        redis_conn.delete(token_hash)
        return Response(tokens)

class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        TokenService.add_token_to_redis(
            request.user.id,
            'fake_token',
            TokenType.ACCESS,
            settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME"),
        )
        TokenService.add_token_to_redis(
            request.user.id,
            'fake_token',
            TokenType.REFRESH,
            settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME"),
        )
        return Response({"detail": _("Successfully logged out")})