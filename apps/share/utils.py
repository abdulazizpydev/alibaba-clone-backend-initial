from typing import Union

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from user.models import Group
from user.models import User, Policy

def add_permissions(obj: Union[User, Group, Policy], permissions: list[str]):
    def get_perm(perm: str) -> list:
        app_label, codename = perm.split('.')
        try:
            model = codename.split('_')[1]
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            permission, _ = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
            )
        except (IndexError, ContentType.DoesNotExist):
            permission, _ = Permission.objects.get_or_create(
                codename=codename
            )
        return permission

    if isinstance(obj, User):
        obj.user_permissions.clear()
        obj.user_permissions.add(*map(get_perm, permissions))
    elif isinstance(obj, Group) or isinstance(obj, Policy):
        obj.permissions.clear()
        obj.permissions.add(*map(get_perm, permissions))