import factory

from django.contrib.auth import get_user_model
from faker import Faker

fake = Faker()

User = get_user_model()


def fake_number():
    country_code = '+99890'
    national_number = fake.numerify(text="#######")
    full_number = country_code + national_number
    return full_number


class UserFactory(factory.django.DjangoModelFactory):
    """This class will create fake data for user"""

    class Meta:
        model = User

    id = factory.Faker('pyint', min_value=1, max_value=100000)
    phone_number = factory.LazyFunction(fake_number)
    email = factory.LazyFunction(fake.email)
    first_name = fake.first_name()
    last_name = fake.last_name()
    gender = fake.random_element(elements=('male', 'female'))
    is_staff = False
    is_active = True
    is_verified = True

    password = factory.PostGenerationMethodCall('set_password', fake.password())
