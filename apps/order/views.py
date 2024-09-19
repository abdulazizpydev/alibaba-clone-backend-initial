from rest_framework import generics, status
from rest_framework.response import Response
from .models import Order
from .serializers import OrderCreateSerializer, OrderSerializer

from share.permissions import GeneratePermissions

from core import settings


class OrderListView(GeneratePermissions, generics.ListAPIView):
    queryset = Order.objects.all()

    def get_serializer_class(self):
        return OrderSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class CheckoutCreateView(GeneratePermissions, generics.CreateAPIView):
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        order = serializer.save(user=request.user)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(GeneratePermissions, generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'pk'

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated and obj.user == self.request.user:
            return obj
        else:
            return None


class OrderHistoryView(GeneratePermissions, generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        """Override to filter orders by the authenticated user."""
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        else:
            return Order.objects.none()

    def get(self, request, *args, **kwargs):
        """Handle GET requests for the user's order history."""
        if not request.user.is_authenticated:
            return None
        return super().get(request, *args, **kwargs)
