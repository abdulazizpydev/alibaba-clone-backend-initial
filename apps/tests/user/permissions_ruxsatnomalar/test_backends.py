import pytest


@pytest.mark.order(1)
@pytest.mark.django_db
def test_backends_exists():
    try:
        from user.backends import CustomModelBackend
    except ImportError:
        assert False, f"CustomModelBackend class is missing"
