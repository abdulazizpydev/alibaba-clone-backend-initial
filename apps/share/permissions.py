from typing import Type, TypeVar

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, BasePermission

BasePermissionType = TypeVar("BasePermissionType", bound=BasePermission)


def check_perm(*permissions) -> Type[BasePermissionType]:
    class CheckPermission(BasePermission):
        def has_permission(self, request, view):
            return request.user.is_superuser or (
                    request.user.is_authenticated
                    and set(permissions).issubset(request.user.get_all_permissions())
            )

    return CheckPermission


class GeneratePermissions(GenericAPIView):
    def generate_permissions(self, *args, **kwargs):
        if getattr(self, "action", None) and self.action in kwargs.keys():
            return kwargs[self.action]
        # return method permission
        if self.request.method and str(self.request.method).lower() in kwargs.keys():
            return kwargs[str(self.request.method).lower()]
        # Create permission by method name
        queryset = self.get_queryset()
        codename = queryset.model.__name__.lower()
        app_name = getattr(queryset.model, "_meta").app_label
        if self.request.method == "POST":
            prefix = "add"
        elif self.request.method == "DELETE":
            prefix = "delete"
        elif self.request.method in ["PUT", "PATCH"]:
            prefix = "change"
        elif self.request.method == "GET":
            prefix = "view"
        else:
            prefix = None
        if not prefix:
            return None
        perm = f"{app_name}.{prefix}_{codename}"
        return perm

    def get_permissions(self, *args, **kwargs):
        if (
                len(self.permission_classes) == 1
                and AllowAny not in self.permission_classes
        ):
            return [permission() for permission in self.permission_classes]
        perm = self.generate_permissions(*args, **kwargs)
        if not perm:
            return self.permission_classes

        permission_classes = [check_perm(perm)]
        return [permission() for permission in permission_classes]
