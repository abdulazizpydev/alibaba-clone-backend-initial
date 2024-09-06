import uuid

from django.db import models
from django.db.models import Index
from django.core.validators import MinValueValidator


class BaseModel(models.Model):
    """
    Abstract base class for other models.

    Provides common fields such as id, created_at, updated_at, is_active, and created_by.
    """

    id = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, primary_key=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="created_%(class)ss",
        limit_choices_to={'is_active': True},
    )

    class Meta:
        abstract = True
        ordering = ["-created_at", "-updated_at"]
        indexes = [
            Index(
                fields=['is_active'],
                name='%(class)s_is_active_idx',
                condition=models.Q(is_active=True)
            )
        ]


class BaseUserInfo(models.Model):
    photo = models.URLField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=100, blank=False, null=False)
    district = models.CharField(max_length=100, blank=False, null=False)
    street_address = models.CharField(max_length=250, blank=False, null=False)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    second_phone_number = models.CharField(max_length=13, blank=True, null=True)
    building_number = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    apartment_number = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])

    id = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, primary_key=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
