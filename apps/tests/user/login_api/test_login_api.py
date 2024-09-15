import pytest


@pytest.fixture
def login_data(request, user_factory):
    password = 'random_password'
    user = user_factory.create(password=password)

    def valid_email():
        user.email = "test@admin.com"
        user.save()
        return (
            200, {
                'email_or_phone_number': user.email,
                'password': password,
            },
        )

    def valid_phone_number():
        user.phone_number = "+998901234568"
        user.save()
        return (
            200, {
                'email_or_phone_number': user.phone_number,
                'password': password,
            },
        )

    def required_username():
        return (
            422, {
                'password': password,
            },
        )

    def empty_username():
        return (
            422, {
                'email_or_phone_number': '',
                'password': password,
            },
        )

    def required_password():
        return (
            422, {
                'email_or_phone_number': user.email,
            },
        )

    def empty_password():
        return (
            422, {
                'email_or_phone_number': user.email,
                'password': '',
            },
        )

    def invalid_password():
        return (
            400, {
                'email_or_phone_number': user.email,
                'password': 'fake_password',
            },
        )

    data = {
        'valid_email': valid_email,
        'valid_phone_number': valid_phone_number,
        'required_username': required_username,
        'empty_username': empty_username,
        'required_password': required_password,
        'empty_password': empty_password,
        'invalid_password': invalid_password,
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'login_data',
    [
        'valid_email',
        'valid_phone_number',
        'required_username',
        'empty_username',
        'required_password',
        'empty_password',
        'invalid_password',
    ],
    indirect=True,
)
def test_login(login_data, api_client):
    status_code, req_json = login_data()
    resp = api_client().post('/api/users/login/', data=req_json)
    assert resp.status_code == status_code
    if status_code == 200:
        resp_json = resp.json()
        assert sorted(resp_json.keys()) == sorted(['access', 'refresh'])
