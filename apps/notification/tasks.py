from celery import shared_task
from notification.models import Notification
from django.contrib.auth import get_user_model
from user.tasks import send_email

User = get_user_model()


@shared_task
def send_notification_task(user_id: int, notification_type: str, message: str):
    """
    Creates a notification for the user and sends an email notification.
    """
    try:
        user = User.objects.get(id=user_id)

        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            message=message,
        )

        send_email.delay(user.email, notification.message)

    except User.DoesNotExist:
        print(f"User with ID {user_id} does not exist.")
    except Exception as e:
        print(f"Error creating notification or sending email: {e}")
