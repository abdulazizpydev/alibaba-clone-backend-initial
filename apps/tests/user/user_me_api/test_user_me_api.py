import pytest

from user.models import User, Group


@pytest.fixture
def user_me_data(request, user_factory, tokens):
    """
    Fixture that returns different sets of data based on the test case.
    """
    user = user_factory.create()
    buyer_group = Group.objects.get(name="buyer")
    user.groups.add(buyer_group)
    user.save()
    access, _ = tokens(user)

    def valid_user():
        return user, access, {
            "first_name": "Abdulaziz",
            "last_name": "Komilov",
            "email": "abdulaziz@example.com",
            "phone_number": "+998931159963",
            "gender": "Male",
            "birth_date": "2024-08-17",
            "github_username": "abdulazizkomilov"
        }, 200

    def empty_first_name():
        return user, access, {"first_name": ""}, 400

    def invalid_string_type():
        return user, access, {
            "first_name": {"foo": "bar"},
        }, 400

    data = {
        'valid_user': valid_user,
        'empty_first_name': empty_first_name,
        'invalid_string_type': invalid_string_type,
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user_me_data',
    [
        'valid_user',
        'empty_first_name',
        'invalid_string_type',
    ],
    indirect=True,
)
def test_user_me(user_me_data, api_client):
    user, access, data, status = user_me_data()

    client = api_client(token=access)
    resp = client.patch('/api/users/me/', data, format='json')
    assert resp.status_code == status

    if status == 200:
        response_data = resp.json()
        for key, value in data.items():
            if key in response_data:
                assert response_data[key] == value


@pytest.fixture
def user_read_data(request, user_factory, tokens):
    user = user_factory()
    buyer_group = Group.objects.get(name="buyer")
    user.groups.add(buyer_group)
    access, refresh = tokens(user)

    def valid_user():
        return 200, access, user.id

    def valid_seller_user():
        seller_user = user_factory()
        seller_group = Group.objects.get(name="seller")
        seller_user.groups.add(seller_group)
        seller_user_access, _ = tokens(seller_user)
        return 200, seller_user_access, seller_user.id

    def inactive_user():
        user.is_active = False
        user.save()
        return 401, access, user.id

    def no_permission():
        user_2 = user_factory()
        access_2, _ = tokens(user_2)
        return 403, access_2, user_2.id

    def unverified_user():
        user_2 = user_factory(is_verified=False)
        access_, _ = tokens(user_2)
        return 403, access_, user_2.id

    data = {
        'valid_user': valid_user,
        'valid_seller_user': valid_seller_user,
        'inactive_user': inactive_user,
        'no_permission': no_permission,
        'unverified_user': unverified_user,
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user_read_data',
    [
        'valid_user',
        'valid_seller_user',
        'inactive_user',
        'no_permission',
        'unverified_user',
    ],
    indirect=True,
)
def test_user_read(request, user_read_data, api_client):
    test_node = request.node.name
    status_code, access, user_id = user_read_data()
    client = api_client(token=access)
    resp = client.get(f'/api/users/me/')
    assert resp.status_code == status_code
    if status_code == 200:
        resp_json = resp.json()
        user_data = ['id', 'first_name', 'last_name', 'phone_number', 'email', 'gender', 'photo', 'bio', 'birth_date',
                     'country', 'city', 'district', 'street_address', 'postal_code', 'second_phone_number',
                     'building_number',
                     'apartment_number']
        if test_node == 'test_user_read[valid_seller_user]':
            user_data.append('company')
            assert sorted(resp_json.keys()) == sorted(
                user_data
            )
        assert sorted(resp_json.keys()) == sorted(
            user_data
        )
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            assert False, "User not found"
        assert resp_json['first_name'] == user.first_name
        assert resp_json['last_name'] == user.last_name
        assert resp_json['phone_number'] == user.phone_number
        assert resp_json['email'] == user.email
