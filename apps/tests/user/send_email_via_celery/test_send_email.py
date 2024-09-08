from django.core import mail
from apps.user.tasks import send_email
import pytest
from core import settings


@pytest.mark.order(1)
def test_send_email_exists():
    try:
        from user.tasks import send_email
    except ImportError:
        assert False, f"send_email function is missing"


@pytest.mark.order(2)
def test_email_config_exists_in_settings():
    assert hasattr(settings, 'EMAIL_BACKEND'), "EMAIL_BACKEND is missing in settings."
    assert getattr(settings, 'EMAIL_BACKEND'), "EMAIL_BACKEND is set but empty."

    assert hasattr(settings, 'EMAIL_HOST'), "EMAIL_HOST is missing in settings."
    assert getattr(settings, 'EMAIL_HOST'), "EMAIL_HOST is set but empty."

    assert hasattr(settings, 'EMAIL_USE_TLS'), "EMAIL_USE_TLS is missing in settings."
    assert getattr(settings, 'EMAIL_USE_TLS'), "EMAIL_USE_TLS is set but empty."

    assert hasattr(settings, 'EMAIL_PORT'), "EMAIL_PORT is missing in settings."
    assert getattr(settings, 'EMAIL_PORT'), "EMAIL_PORT is set but empty."

    assert hasattr(settings, 'EMAIL_HOST_USER'), "EMAIL_HOST_USER is missing in settings."
    assert getattr(settings, 'EMAIL_HOST_USER'), "EMAIL_HOST_USER is set but empty."

    assert hasattr(settings, 'EMAIL_HOST_PASSWORD'), "EMAIL_HOST_PASSWORD is missing in settings."
    assert getattr(settings, 'EMAIL_HOST_PASSWORD'), "EMAIL_HOST_PASSWORD is set but empty."


@pytest.mark.order(3)
@pytest.mark.django_db
def test_send_email_success():
    email = 'test@example.com'
    otp_code = '123456'
    result = send_email(email, otp_code)

    assert result == 200
    assert len(mail.outbox) == 1


@pytest.mark.order(4)
@pytest.mark.django_db
def test_send_email_failure(mocker):
    mocker.patch('django.core.mail.EmailMessage.send', side_effect=Exception('Xato!'))

    email = 'test@example.com'
    otp_code = '123456'
    result = send_email(email, otp_code)

    assert result == 400
