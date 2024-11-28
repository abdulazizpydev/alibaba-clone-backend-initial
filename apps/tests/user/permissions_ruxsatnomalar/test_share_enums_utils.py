import pytest


@pytest.mark.order(1)
@pytest.mark.django_db
def test_enums_exists():
    try:
        from share import enums
    except ImportError:
        assert False, f"enums file is missing"


@pytest.mark.order(2)
@pytest.mark.django_db
def test_enums_user_role_exists():
    try:
        from share.enums import UserRole
    except ImportError:
        assert False, f"UserRole enum is missing"


@pytest.mark.order(3)
@pytest.mark.django_db
def test_enums_policy_name_exists():
    try:
        from share.enums import PolicyNameEnum
    except ImportError:
        assert False, f"PolicyNameEnum enum is missing"


@pytest.mark.order(4)
@pytest.mark.django_db
def test_utils_exists():
    try:
        from share import utilssss
    except ImportError:
        assert False, f"utils file is missing"


@pytest.mark.order(5)
@pytest.mark.django_db
def test_utils_add_permissions_exists():
    try:
        from share.utils import add_permissions
    except ImportError:
        assert False, f"add_permissions function is missing"
