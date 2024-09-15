from rest_framework.views import APIView
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from .models import Cart, CartItem
from .serializers import CartItemSerializer
from share.permissions import GeneratePermissions
from django.shortcuts import get_object_or_404


class GetItemsView(GeneratePermissions, generics.ListAPIView):
    """
    Retrieves the items in the cart for the authenticated user.
    """

    serializer_class = CartItemSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return CartItem.objects.none()

        cart, _ = Cart.objects.get_or_create(user=user)
        return CartItem.objects.filter(cart=cart).order_by('product')

    @extend_schema(
        responses={200: CartItemSerializer(many=True)},
        tags=['cart']
    )
    def get(self, request, *args, **kwargs):
        try:
            cart_items = self.get_queryset()
            serializer = self.get_serializer(cart_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except exceptions.PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            print(f"Failed to retrieve cart items: {e}")
            return Response(
                {'detail': 'Something went wrong when retrieving cart items'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddItemView(GeneratePermissions, generics.CreateAPIView):
    """
    Adds an item to the cart for the authenticated user.
    """

    serializer_class = CartItemSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return CartItem.objects.none()

        cart, _ = Cart.objects.get_or_create(user=user)
        return CartItem.objects.filter(cart=cart)

    @extend_schema(
        request=CartItemSerializer,
        responses={
            201: CartItemSerializer(many=True),
            400: OpenApiExample('Bad Request', value={'error': 'Invalid data provided'})
        },
        tags=['cart']
    )
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'User is not authenticated'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        serializer.save()

        cart_items = self.get_queryset().order_by('product')
        result = CartItemSerializer(cart_items, many=True).data

        return Response(result, status=status.HTTP_201_CREATED)


class UpdateItemQuantityView(GeneratePermissions, APIView):
    """
    Updates the quantity of a specific item in the cart for the authenticated user.
    """

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return CartItem.objects.none()

        cart, _ = Cart.objects.get_or_create(user=user)
        return CartItem.objects.filter(cart=cart)

    @extend_schema(
        request=CartItemSerializer,
        responses={
            200: CartItemSerializer,
            400: OpenApiExample('Bad Request', value={'error': 'Invalid quantity or product'}),
            404: OpenApiExample('Not Found', value={'detail': 'Cart item not found'}),
        },
        tags=['cart']
    )
    def patch(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')
        new_quantity = request.data.get('quantity')

        if not user.is_authenticated:
            return Response(
                {'detail': 'User is not authenticated'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not product_id or new_quantity is None:
            return Response(
                {'detail': 'Product ID and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the cart for the authenticated user
        cart, _ = Cart.objects.get_or_create(user=user)

        # Retrieve the specific cart item or return a 404 error if not found
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

        if new_quantity <= 0:
            return Response(
                {'detail': 'Quantity must be greater than zero'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the quantity of the cart item
        cart_item.quantity = new_quantity
        cart_item.save()

        # Serialize the updated cart item
        serializer = CartItemSerializer(cart_item)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GetCartTotalView(GeneratePermissions, APIView):
    """
    Retrieves the total cost of the cart for the authenticated user.
    """

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return CartItem.objects.none()

        cart, _ = Cart.objects.get_or_create(user=user)
        return CartItem.objects.filter(cart=cart)

    @extend_schema(
        responses={200: {'type': 'object', 'properties': {'total': {'type': 'number'}}}},
    )
    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)

            total_quantity = sum(item.quantity for item in cart_items)
            total_price = sum(item.quantity * item.product.price for item in cart_items)

            data = {
                'total_items': cart_items.count(),
                'total_quantity': total_quantity,
                'total_price': total_price,
            }
            return Response(data, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)


class RemoveItemView(GeneratePermissions, generics.DestroyAPIView):
    """
    Removes an item from the cart for the authenticated user.
    """
    serializer_class = CartItemSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return CartItem.objects.none()

        cart, _ = Cart.objects.get_or_create(user=user)
        return CartItem.objects.filter(cart=cart)

    def get_object(self):
        user = self.request.user
        product_id = self.kwargs.get('product_id')
        cart = get_object_or_404(Cart, user=user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        return cart_item

    @extend_schema(
        responses={204: None},
        tags=['cart']
    )
    def delete(self, request, *args, **kwargs):
        try:
            cart_item = self.get_object()
            cart_item.delete()

            cart = cart_item.cart
            cart.total_items = CartItem.objects.filter(cart=cart).count()
            cart.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except exceptions.NotFound as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Failed to remove cart item: {e}")
            return Response(
                {'detail': 'Something went wrong when removing the cart item'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmptyCartView(GeneratePermissions, generics.DestroyAPIView):
    """
    Empties the cart for the authenticated user.
    """

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return CartItem.objects.none()

        cart, _ = Cart.objects.get_or_create(user=user)
        return CartItem.objects.filter(cart=cart)

    @extend_schema(
        responses={204: None},
        tags=['cart']
    )
    def delete(self, request, *args, **kwargs):
        try:
            user = request.user
            cart = get_object_or_404(Cart, user=user)

            cart.items.all().delete()

            cart.total_items = 0
            cart.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"Failed to empty the cart: {e}")
            return Response(
                {'detail': 'Something went wrong when emptying the cart'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
