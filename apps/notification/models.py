from django.db import models
from django.contrib.auth import get_user_model
from share.models import BaseModel
from share.enums import NotificationType

User = get_user_model()


class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50, choices=NotificationType.choices())
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.full_name} - {self.type}"
