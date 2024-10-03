from django.contrib import admin
from .models import User, Policy, BuyerUser, SellerUser
from user.models import Group as UserGroup

admin.site.register(BuyerUser)
admin.site.register(SellerUser)


@admin.register(User)
class UserAdminManager(admin.ModelAdmin):
    def group(self, user):
        groups = []
        for group in user.groups.filter(is_active=True):
            groups.append(group.name)
        return ';'.join(groups)

    group.short_description = 'Groups'

    list_display = [
        "id",
        "first_name",
        "last_name",
        "phone_number",
        "email",
        "group",
        "is_active",
        "is_verified",
        "is_staff",
        "is_superuser",
        "last_login",
        "date_joined",
    ]
    list_filter = [
        "groups__name",
        "is_staff",
        "is_verified",
        "is_superuser",
        "is_active",
        "date_joined",
        "last_login",
    ]
    search_fields = ["first_name", "last_name", "email", "phone_number"]
    filter_horizontal = ("user_permissions", "groups", "policies")


@admin.register(UserGroup)
class GroupAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "is_active",
    ]
    search_fields = [
        "name",
    ]
    list_filter = ["created_at", "is_active"]
    list_display_links = ["id", "name"]
    filter_horizontal = ("permissions", "policies")


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "is_active",
    ]
    search_fields = [
        "name",
    ]
    list_filter = ["created_at", "is_active"]
    list_display_links = ["id", "name"]
    filter_horizontal = ("permissions",)
