import pytest
from rest_framework import status
from user.models import Group


@pytest.mark.django_db
class TestProductCreateAPI:
    @pytest.fixture(autouse=True)
    def setup(self, api_client, user_factory, tokens, category_factory):
        self.user = user_factory()
        seller_group = Group.objects.get(name="seller")
        self.user.groups.add(seller_group)
        self.user.save()

        self.access, _ = tokens(self.user)
        self.client = api_client(self.access)

        self.category = category_factory(name="Electronics")

        self.url = '/products/'

    @pytest.mark.parametrize("payload, expected_status", [
        ({
             "category": 1,
             "seller": 1,
             "title": "New Product",
             "min_price": 100,
             "max_price": 200,
             "description": "A great product"
         },
         status.HTTP_201_CREATED),
        ({
             "category": 1,
             "seller": 1,
             "title": "Another Product",
             "min_price": 150,
             "max_price": 250,
             "description": "Another great product"
         },
         status.HTTP_201_CREATED),
    ])
    def test_create_new_product(self, payload, expected_status):
        payload['category'] = self.category.id
        payload['seller'] = self.user.id

        response = self.client.post(self.url, data=payload, format='json')
        assert response.status_code == expected_status
        if response.status_code == status.HTTP_201_CREATED:
            assert response.json()['title'] == payload['title']
            assert response.json()['min_price'] == payload['min_price']
            assert response.json()['max_price'] == payload['max_price']

    @pytest.mark.parametrize("payload, expected_status", [
        ({}, status.HTTP_400_BAD_REQUEST),
        ({"title": ""}, status.HTTP_400_BAD_REQUEST),
        ({"min_price": 100}, status.HTTP_400_BAD_REQUEST),
        ({
             "title": "Incomplete Product",
             "min_price": -10,
             "max_price": -20
         }, status.HTTP_400_BAD_REQUEST),
    ])
    def test_invalid_product_data(self, payload, expected_status):
        response = self.client.post(self.url, data=payload, format='json')
        assert response.status_code == expected_status
        assert 'errors' in response.json() or response.status_code == status.HTTP_400_BAD_REQUEST

    def test_required_fields(self):
        response = self.client.post(self.url, data={"description": "Missing category and title"}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.json()
        assert 'category' in errors or 'title' in errors

    def test_user_without_permission(self, user_factory, tokens, api_client):
        self.user = user_factory()
        buyer_group = Group.objects.get(name="buyer")
        self.user.groups.add(buyer_group)
        self.user.save()

        access, _ = tokens(self.user)
        client = api_client(access)

        payload = {
            "category": self.category.id,
            "seller": self.user.id,
            "title": "Product",
            "min_price": 100,
            "max_price": 200,
            "description": "A product by no permission user"
        }
        response = client.post(self.url, data=payload, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_product_without_images(self):
        payload = {
            "category": self.category.id,
            "seller": self.user.id,
            "title": "Coffee Machine Without Images",
            "min_price": 89.3,
            "max_price": 93.2,
            "description": "A professional espresso coffee maker without images",
            "colors": [
                {"name": "Black", "hex_value": "#000000"}
            ],
            "sizes": [
                {"name": "Small", "description": "Small size"}
            ],
            "quantity": 10
        }

        response = self.client.post(self.url, data=payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data['title'] == payload['title']
        assert len(response_data['images']) == 0
        assert response_data['colors'][0]['name'] == "black"
        assert response_data['sizes'][0]['name'] == "small"
        assert response_data['quantity'] == payload['quantity']
        assert len(response_data['colors']) == len(payload['colors'])
        assert len(response_data['sizes']) == len(payload['sizes'])
