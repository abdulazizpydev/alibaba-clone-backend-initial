from rest_framework import generics
from .models import Notification
from .serializers import NotificationSerializer, NotificationUpdateSerializer
from share.permissions import GeneratePermissions


class NotificationListView(GeneratePermissions, generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class RetrieveUpdateView(GeneratePermissions, generics.RetrieveUpdateAPIView):
    http_method_names = ['get', 'patch']
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return NotificationUpdateSerializer
        return NotificationSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)

    def get_object(self):
        notification = super().get_object()
        if notification.user == self.request.user:
            return notification
        return None
