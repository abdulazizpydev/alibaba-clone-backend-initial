from share.permissions import GeneratePermissions
from rest_framework import status, generics
from .models import Wishlist
from .serializers import WishlistSerializer


class WishlistListCreateView(GeneratePermissions, generics.ListCreateAPIView):
    """
    View to list user's wishlist and add items to wishlist.
    """
    serializer_class = WishlistSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Wishlist.objects.none()
        return Wishlist.objects.filter(created_by=self.request.user)


class WishlistRetrieveDeleteView(GeneratePermissions, generics.RetrieveDestroyAPIView):
    """
    View to remove an item from the wishlist.
    """
    serializer_class = WishlistSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Wishlist.objects.none()
        return Wishlist.objects.filter(created_by=self.request.user)

    def get_object(self):
        return generics.get_object_or_404(Wishlist, created_by=self.request.user, id=self.kwargs['pk'])
