import pytest
from core import settings


@pytest.mark.order(1)
def test_celery_exists():
    try:
        from core import celery
    except ImportError:
        assert False, f"celery file is missing"


@pytest.mark.order(2)
def test_celery_app_exists():
    try:
        from core.celery import app
    except ImportError:
        assert False, f"app is missing in core.celery file"


@pytest.mark.order(3)
def test_celery_config_exists_in_settings():
    assert hasattr(settings, 'CELERY_BROKER_URL'), "CELERY_BROKER_URL is missing in settings."
    assert getattr(settings, 'CELERY_BROKER_URL'), "CELERY_BROKER_URL is set but empty."

    assert hasattr(settings, 'CELERY_RESULT_BACKEND'), "CELERY_RESULT_BACKEND is missing in settings."
    assert getattr(settings, 'CELERY_RESULT_BACKEND'), "CELERY_RESULT_BACKEND is set but empty."

    assert hasattr(settings, 'CELERY_TIMEZONE'), "CELERY_TIMEZONE is missing in settings."
    assert getattr(settings, 'CELERY_TIMEZONE'), "CELERY_TIMEZONE is set but empty."
