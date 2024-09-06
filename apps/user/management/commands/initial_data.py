import yaml

from core.settings import config
from django.core.management.base import BaseCommand

from share.enums import UserRole, PolicyNameEnum
from share.utils import add_permissions
from user.models import Policy, User, Group

class Command(BaseCommand):
    help = 'Create initial data, including user groups and policies'

    def handle(self, *args, **options):
        self.create_superuser()
        self.create_default_policies()
        for group_name in [UserRole.BUYER.value, UserRole.SELLER.value, UserRole.ADMIN.value]:
            group_obj, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'{group_name} group created successfully'))
            policy_name = f"{group_name}_policy"
            if policy_name not in PolicyNameEnum.values():
                self.stdout.write(self.style.ERROR(
                    f"{policy_name} not exists in available policy names. Add new policy name to PolicyNameEnum")
                )
                return
            policy = Policy.objects.get(name=f"{group_name}_policy", is_active=True)
            group_obj.policies.add(policy)
        self.stdout.write(self.style.SUCCESS('Initial data creation complete'))

    def create_superuser(self):
        superuser_email = config('DJANGO_SUPERUSER_EMAIL')
        superuser_password = config('DJANGO_SUPERUSER_PASSWORD')
        if not User.objects.filter(email=superuser_email).exists():
            User.objects.create_superuser(email=superuser_email, password=superuser_password)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))

    def create_default_policies(self):
        with open('.fixtures/policies.yaml', 'r', encoding='utf-8') as file:
            policies_data = yaml.safe_load(file)
            if policies_data:
                for policy_name, permissions in policies_data.items():
                    if policy_name not in PolicyNameEnum.values():
                        self.stdout.write(self.style.ERROR(
                            f"{policy_name} not exists in available policy names. Add new policy name to PolicyNameEnum")
                        )
                        return
                    policy, is_created = Policy.objects.get_or_create(name=policy_name, is_active=True)
                    self.stdout.write(self.style.SUCCESS(
                        f'{policy_name} policy created successfully with {len(permissions)} permissions')
                    )
                    add_permissions(policy, permissions)