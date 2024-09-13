import pytest
from rest_framework import status
from user.models import Group
from product.models import Product


@pytest.mark.django_db
class TestProductListAPI:
    @pytest.fixture(autouse=True)
    def setup(self, api_client, tokens, user_factory, category_factory, product_factory):
        self.user = user_factory()
        buyer_group = Group.objects.get(name="buyer")
        self.user.groups.add(buyer_group)
        self.user.save()

        self.access, _ = tokens(self.user)

        self.client = api_client(self.access)
        self.url = '/api/products/'

        self.category = category_factory(name="Electronics")
        self.product1 = product_factory(title="product1", category=self.category)
        self.product2 = product_factory(title="product2", category=self.category)
        self.product3 = product_factory(title="product3", category=self.category)

    @pytest.mark.parametrize("search_query, expected_count", [
        ("product1", 1),
        ("product", 3),
        ("nonexistent", 0),
    ])
    def test_product_list_retrieved_successfully(self, search_query, expected_count):
        response = self.client.get(self.url, {'search': search_query})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == expected_count

    def test_empty_product_list(self):
        Product.objects.all().delete()
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == []

    @pytest.mark.parametrize("product_id, recommend_count, expected_min_count", [
        ("product1", 2, 1),
        ("product1", 1, 1),
        ("product2", 3, 1),
    ])
    def test_recommend_products_by_product_id(self, product_id, recommend_count, expected_min_count):
        product_mapping = {
            "product1": self.product1.id,
            "product2": self.product2.id,
        }

        target_product_id = str(product_mapping[product_id])

        response = self.client.get(self.url, {
            'recommend_by_product_id': target_product_id,
            'recommend': recommend_count
        })

        assert response.status_code == status.HTTP_200_OK

        product_ids = [product["id"] for product in response.data['results']]

        assert target_product_id not in product_ids, f"Product {target_product_id} should not be in recommendations"

        assert len(response.data['results']) >= expected_min_count, (
            f"Expected at least {expected_min_count} products, got {len(response.data['results'])}"
        )

    def test_recommend_products_invalid_product_id(self):
        response = self.client.get(self.url,
                                   {'recommend_by_product_id': '00000000-0000-0000-0000-000000000000', 'recommend': 2})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == []

    def test_recommend_products_no_recommend_param(self):
        response = self.client.get(self.url, {'recommend_by_product_id': str(self.product1.id)})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
