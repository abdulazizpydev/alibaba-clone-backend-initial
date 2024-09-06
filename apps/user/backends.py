from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission

class CustomModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username:
            return None
        try:
            if "@" in username:
                username_field = "email"
            else:
                username_field = "phone_number"
            user = get_user_model().objects.get(**{username_field: username})
        except get_user_model().DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

    def user_can_authenticate(self, user):
        return user.is_active and user.is_verified

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None

    def _get_user_permissions(self, user_obj):
        all_user_permissions = user_obj.user_permissions.all()
        for policy in user_obj.policies.filter(is_active=True):
            all_user_permissions |= policy.permissions.all()
        return all_user_permissions

    def _get_group_permissions(self, user_obj):
        user_groups_field = get_user_model()._meta.get_field("groups")
        user_groups_query = "custom_group__%s" % user_groups_field.related_query_name()
        all_group_permissions = Permission.objects.filter(**{user_groups_query: user_obj})
        for group in user_obj.groups.filter(is_active=True):
            for policy in group.policies.filter(is_active=True):
                all_group_permissions |= policy.permissions.all()
        return all_group_permissions