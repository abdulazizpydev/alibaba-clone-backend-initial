import pytest
from rest_framework import status
from user.models import Group


@pytest.mark.django_db
class TestCategoryViewSet:

    @pytest.fixture(autouse=True)
    def setup(self, user_factory, tokens, api_client):
        self.api = '/products/categories/'

        # Setup for the buyer user
        self.user = user_factory()
        buyer_group = Group.objects.get(name="buyer")
        self.user.groups.add(buyer_group)
        self.user.save()

        self.access, _ = tokens(self.user)
        self.client = api_client(token=self.access)

        # Setup for an additional buyer user
        self.buyer_user = user_factory()
        self.buyer_access, _ = tokens(self.buyer_user)
        self.buyer_client = api_client(token=self.buyer_access)

        # Setup for the seller user
        self.seller_user = user_factory()
        seller_group = Group.objects.get(name="seller")
        self.seller_user.groups.add(seller_group)
        self.seller_user.save()

        self.seller_access, _ = tokens(self.seller_user)
        self.seller_client = api_client(token=self.seller_access)

    @pytest.mark.parametrize(
        'client, expected_status, expected_count',
        [
            ('client', status.HTTP_200_OK, 5),
            ('seller_client', status.HTTP_200_OK, 5)
        ]
    )
    def test_list_categories(self, category_factory, client, expected_status, expected_count):
        # Create 5 categories
        category_factory.create_batch(expected_count)

        # Send GET request to list categories
        response = getattr(self, client).get(self.api)
        assert response.status_code == expected_status
        assert len(response.data['results']) == expected_count
        # Additional checks on response data structure
        assert all('id' in category and 'name' in category for category in response.data['results'])

    @pytest.mark.parametrize(
        'search_query, expected_count',
        [
            ('Electronics', 1),
            ('Books', 1),
            ('Nonexistent', 0)
        ]
    )
    def test_list_categories_with_search(self, category_factory, search_query, expected_count):
        # Create specific categories
        category_factory.create(name="Electronics")
        category_factory.create(name="Books")

        # Search for the query
        response = self.client.get(self.api, {'search': search_query})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == expected_count
        if expected_count > 0:
            assert response.data['results'][0]['name'] == search_query

    def test_retrieve_single_category(self, category_factory):
        # Create a single category
        category = category_factory.create()

        # Retrieve the category by ID
        response = self.client.get(f'{self.api}{category.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(category.id)

    @pytest.mark.parametrize(
        'category_id, expected_status',
        [
            ('999999', status.HTTP_404_NOT_FOUND),
            ('incorrect-id', status.HTTP_404_NOT_FOUND)
        ]
    )
    def test_retrieve_invalid_category(self, category_id, expected_status):
        # Try retrieving a non-existent or invalid category
        response = self.client.get(f'{self.api}{category_id}/')
        assert response.status_code == expected_status

    def test_unauthorized_access(self, api_client):
        # Try accessing the endpoint without authentication
        client = api_client()
        response = client.get(self.api)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_category_products(self, category_factory, product_factory):
        # Create a category and products within that category
        category = category_factory.create()
        product_factory.create_batch(3, category=category)

        # Retrieve the products of the category
        response = self.client.get(f'{self.api}{category.id}/products/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_no_permissions(self, category_factory):
        # Create a category
        category = category_factory.create(name="Electronics")

        # Try retrieving the products of the category with a non-permitted user
        response = self.buyer_client.get(f'{self.api}{category.id}/products/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_seller_access(self, category_factory):
        # Create a category
        category_factory.create(name="Electronics")

        # Ensure seller can access the list categories endpoint
        response = self.seller_client.get(self.api)
        assert response.status_code == status.HTTP_200_OK
