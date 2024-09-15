from rest_framework import permissions, status, generics
from rest_framework.exceptions import PermissionDenied, NotAcceptable, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, filters as drf_filters, status
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from share.permissions import GeneratePermissions, check_perm
from django.db.models import F
from rest_framework import viewsets, mixins
from rest_framework.decorators import action

from .serializers import *
from .filters import ProductFilter
from .models import Product, ProductViews


class CategoryViewSet(GeneratePermissions, viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("name", "parent__name", "children__name")

    @extend_schema(
        description="Retrieve a list of categories.",
        parameters=[
            OpenApiParameter(name='search', description='Search term', required=False, type=str),
        ],
        responses={200: CategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """
        List all categories with an optional search feature.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Retrieve a single category by ID.",
        responses={200: CategorySerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single category by its ID.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='products', url_name='category-products')
    @extend_schema(
        description="Retrieve all products belonging to a specific category.",
        responses={200: ProductSerializer(many=True)}
    )
    def get_category_products(self, request, pk=None):
        """
        Retrieve all products belonging to a specific category.
        """
        category = self.get_object()
        products = Product.objects.filter(category=category)  # Adjust if your model relationships differ
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """
        Override to filter parent categories if listing categories.
        """
        if self.action == 'list':
            return Category.objects.filter(parent=None)
        return super().get_queryset()


class ProductListAPIView(GeneratePermissions, generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    filter_backends = (
        DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    )
    search_fields = ("title", "description",)
    filterset_class = ProductFilter
    ordering_fields = ("created_at", "views")
    queryset = Product.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateProductSerializer
        return ProductSerializer

    @extend_schema(
        description="Retrieve a list of products or recommended products based on a category.",
        parameters=[
            OpenApiParameter(name='search', description='Search term', required=False, type=str),
            OpenApiParameter(name='recommend_by_product_id', description='ID of the product for recommendations',
                             required=False,
                             type='uuid'),
        ],
        responses={200: ProductSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        recommend_by_product_id = request.query_params.get('recommend_by_product_id')

        if recommend_by_product_id:
            try:
                product = Product.objects.get(id=recommend_by_product_id)
                queryset = queryset.filter(category=product.category).exclude(id=recommend_by_product_id).order_by(
                    '-views')
            except Product.DoesNotExist:
                queryset = Product.objects.none()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductDetailView(GeneratePermissions, generics.CreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ['get', 'patch', 'put', 'delete']

    def get_queryset(self):
        return Product.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return CreateProductSerializer
        return ProductDetailSerializer

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    @extend_schema(
        description="Retrieve product details by ID.",
        responses={200: ProductDetailSerializer}
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        product = self.get_object()
        ip = self.get_client_ip(request)

        if not ProductViews.objects.filter(product=product, ip=ip).exists():
            ProductViews.objects.create(product=product, ip=ip)
            product.views = F('views') + 1
            product.save(update_fields=["views"])

        return response

    @extend_schema(
        description="Update product details by ID.",
        request=ProductDetailSerializer,
        responses={200: ProductDetailSerializer}
    )
    def patch(self, request, *args, **kwargs):
        product = self.get_object()
        if product.seller != request.user:
            raise PermissionDenied("This product doesn't belong to you.")

        request_data = request.data.copy()
        if 'seller' not in request_data:
            request_data['seller'] = request.user.id

        return super().partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        if request.user != product.seller:
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        product = self.get_object()
        if request.user != product.seller:
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(product, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
