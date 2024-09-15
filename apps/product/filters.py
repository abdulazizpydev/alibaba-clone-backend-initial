from django_filters import rest_framework as filters
from .models import Product


class ProductFilter(filters.FilterSet):
    recommend_by_product_id = filters.UUIDFilter(method='filter_by_recommend')

    class Meta:
        model = Product
        fields = ['recommend_by_product_id', ]

    def filter_by_recommend(self, queryset, name, value):

        product_id = self.request.query_params.get('product_id')
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                return queryset.filter(category=product.category).exclude(id=product_id).order_by('-views')
            except Product.DoesNotExist:
                return queryset.none()
        return queryset
