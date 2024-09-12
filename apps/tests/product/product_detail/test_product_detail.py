import pytest
from rest_framework import status
from user.models import Group


@pytest.mark.django_db
class TestProductAPIs:
    @pytest.fixture(autouse=True)
    def setup(self, api_client, user_factory, tokens, category_factory, product_factory):
        self.seller_user = user_factory()
        seller_group = Group.objects.get(name="seller")
        self.seller_user.groups.add(seller_group)
        self.seller_user.save()

        self.access, _ = tokens(self.seller_user)
        self.seller_client = api_client(self.access)

        self.buyer_user = user_factory()
        buyer_group = Group.objects.get(name="buyer")
        self.buyer_user.groups.add(buyer_group)
        self.buyer_user.save()

        self.seller_user_2 = user_factory()
        seller_group = Group.objects.get(name="seller")
        self.seller_user_2.groups.add(seller_group)
        self.seller_user_2.save()

        self.access, _ = tokens(self.seller_user_2)
        self.seller_client_2 = api_client(self.access)

        self.access, _ = tokens(self.buyer_user)
        self.buyer_client = api_client(self.access)

        self.category = category_factory(name="Electronics")
        self.product = product_factory(category=self.category, seller=self.seller_user, title="Sample Product")

        self.url = '/products/'

    def test_get_product_detail_unauthorized(self, api_client):
        client = api_client()
        response = client.get(f'{self.url}{self.product.id}/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_product_no_permission(self):
        response = self.buyer_client.delete(f'{self.url}{self.product.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_put_product_no_permission(self):
        response = self.buyer_client.put(f'{self.url}{self.product.id}/', data={}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_patch_product_no_permission(self):
        response = self.buyer_client.patch(f'{self.url}{self.product.id}/', data={}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_with_no_author_product_no_permission(self):
        response = self.seller_client_2.delete(f'{self.url}{self.product.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_patch_with_no_author_product_no_permission(self):
        response = self.seller_client_2.patch(f'{self.url}{self.product.id}/', data={}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_put_with_no_author_product_no_permission(self):
        response = self.seller_client_2.put(f'{self.url}{self.product.id}/', data={}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_patch_product_with_empty_fields(self):
        patch_data = {
            "title": "",
        }
        response = self.seller_client.patch(f'{self.url}{self.product.id}/', data=patch_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.json()

    def test_put_product_with_empty_fields(self):
        put_data = {
            "category": str(self.category.id),
            "seller": str(self.seller_user.id),
            "title": "",
            "min_price": 0,
            "max_price": 0,
            "description": "",
            "quantity": 0
        }
        response = self.seller_client.put(f'{self.url}{self.product.id}/', data=put_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.json()

        valid_data = put_data.copy()
        valid_data.update({'title': 'Sample Product'})
        response = self.seller_client.put(f'{self.url}{self.product.id}/', data=valid_data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_put_product_with_missing_required_fields(self):
        put_data = {
            "category": str(self.category.id),
            "seller": str(self.seller_user.id),
        }
        response = self.seller_client.put(f'{self.url}{self.product.id}/', data=put_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.json()

    def test_get_product_details(self):
        response = self.buyer_client.get(f'{self.url}{self.product.id}/')
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data['title'] == self.product.title
        assert response_data['description'] == self.product.description

    def test_delete_product(self):
        response = self.seller_client.delete(f'{self.url}{self.product.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = self.seller_client.get(f'{self.url}{self.product.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
