from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from order.models import Order
from share.permissions import GeneratePermissions
from .serializers import CouponSerializer, CouponListSerializer, CouponCreateSerializer
from rest_framework import generics
from .models import Coupon


class CouponListView(GeneratePermissions, generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CouponListSerializer
        return CouponCreateSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Coupon.objects.none()
        return Coupon.objects.filter(active=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ApplyCouponView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CouponSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            coupon = serializer.validated_data['coupon_code']
            order_id = serializer.validated_data['order_id']

            try:
                order = Order.objects.get(id=order_id, user=request.user, status='pending')
            except Order.DoesNotExist:
                return Response({"error": "Order not found or not accessible."}, status=status.HTTP_404_NOT_FOUND)

            print("order amount: ", order.amount)
            total_price = order.amount
            discount_amount = coupon.apply_coupon(total_price)
            print("discount amount: ", discount_amount)

            order.amount = discount_amount
            order.coupon = coupon
            order.save()

            coupon.users.add(request.user)
            coupon.apply()
            coupon.save()

            return Response({"detail": "Coupon applied successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CouponDetailView(GeneratePermissions, generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ['patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'DELETE':
            return None
        return CouponCreateSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Coupon.objects.none()
        return Coupon.objects.filter(active=True)

    def patch(self, request, *args, **kwargs):
        coupon = self.get_object()
        serializer = self.get_serializer(coupon, data=request.data, partial=True)  # Partial updates
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        coupon = self.get_object()
        self.perform_destroy(coupon)
        return Response(status=status.HTTP_204_NO_CONTENT)
