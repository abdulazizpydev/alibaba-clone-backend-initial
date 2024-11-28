from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import Permission, PermissionsMixin, GroupManager
from django.contrib.postgres.indexes import HashIndex
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from user.managers import CustomUserManager

from share.enums import UserRole, GenderChoices, PolicyNameEnum
from share.models import BaseModel, BaseUserInfo


def user_directory_path(instance, filename):
    return f"users/{instance.user.username}/{filename}"


def national_image_path(instance, filename):
    return f"national/{instance.user.username}/images/{filename}"


class Group(BaseModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=150, unique=True)
    policies = models.ManyToManyField("user.Policy", blank=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("permissions"),
        blank=True,
        related_name="custom_group",
    )
    objects = GroupManager()

    class Meta:
        db_table = "group"
        verbose_name = _("Group")
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Users(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    A user in the system.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=13, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    policies = models.ManyToManyField("user.Policy", blank=True)
    gender = models.CharField(
        max_length=10, null=True, blank=True, choices=GenderChoices.choices()
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="user_set",
        related_query_name="user",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "id"

    class Meta:
        db_table = "user"
        verbose_name = _("User")
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=~Q(email=None, phone_number=None),
                name="check_email_or_phone_number",
            )
        ]
        indexes = [
            HashIndex(fields=['first_name'], name='%(class)s_first_name_hash_idx'),
            HashIndex(fields=['last_name'], name='%(class)s_last_name_hash_idx'),
            models.Index(fields=['phone_number'], name='%(class)s_phone_number_idx'),
            models.Index(fields=['email'], name='%(class)s_email_idx'),
        ]
        permissions = [
            ("view_all_users", "Can view all users"),
            ("view_user_me", "Can view user me"),
            ("change_user_me", "Can change user me"),
        ]

    def __str__(self):
        """
        Returns a string representation of the user.

        Returns:
            str: The string representation of the user.
        """
        return self.email

    def __repr__(self):
        return "User object [id={id} username={username} full_name={full_name}]".format(
            id=self.id,
            full_name=self.full_name,
            username=self.email,
        )

    @property
    def username(self):
        """
        Returns the user's username.

        Returns:
            str: The user's username.
        """
        return self.email or self.phone_number

    @property
    def full_name(self):
        """
        Returns the user's full name.

        Returns:
            str: The user's full name.
        """
        return f"{self.last_name} {self.first_name}"

    def is_roles_exists(self, *roles: UserRole) -> bool:
        return self.groups.filter(name__in=[role.value for role in roles], is_active=True).exists()


class Policy(BaseModel):
    name = models.CharField(max_length=100, choices=PolicyNameEnum.choices())
    permissions = models.ManyToManyField(Permission)

    class Meta:
        db_table = "policy"
        verbose_name = _("Policy")
        verbose_name_plural = _("Policies")
        ordering = ['-created_at']
        indexes = [
            HashIndex(
                fields=['name'], name='%(class)s_name_hash_idx'
            )
        ]
        constraints = [
            models.UniqueConstraint(fields=['name', 'is_active'],
                                    name='%(class)s_unique_name_is_active')
        ]

    def get_permissions_set(self):
        return {f"{perm.content_type.app_label}.{perm.codename}" for perm in self.permissions.all()}

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Policy object [id={id} name={name}]".format(
            id=self.id,
            name=self.name,
        )


class SellerUser(BaseUserInfo):
    user = models.OneToOneField(User, related_name="seller_profile", on_delete=models.CASCADE)
    company = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.id}"


class BuyerUser(BaseUserInfo):
    user = models.OneToOneField(User, related_name="buyer_profile", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.id}"
