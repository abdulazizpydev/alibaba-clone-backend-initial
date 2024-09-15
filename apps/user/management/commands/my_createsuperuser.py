from getpass import getpass

import phonenumbers
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from phonenumbers import NumberParseException

from share.utils import CustomPasswordValidator
from user.models import User
from django.contrib.auth.management.commands import createsuperuser


class Command(createsuperuser.Command):
    """
    The class for creating a superuser

    Example:
    python manage.py my_createsuperuser
    OR
    python manage.py my_createsuperuser --no-input --email yakubov9791999@gmail.com --password 123456
    """

    help = 'Create a superuser with additional prompts'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--phone-number',
            dest='phone_number',
            default=None,
            help='Specifies the phone number for the superuser.',
        )
        parser.add_argument(
            '--email',
            dest='email',
            default=None,
            help='Specifies the email for the superuser.',
        )
        parser.add_argument(
            '--password',
            dest='password',
            default=None,
            help='Specifies the password for the superuser.',
        )

    def handle(self, *args, **options):
        """
        This function prompts the user to enter an email or phone number to use as a username,
        then creates a superuser with the provided information.
        """
        if options.get('interactive', True):
            self.stdout.write(
                self.style.SUCCESS(
                    'Enter an email or phone number to use as a username!'
                )
            )
        # Collecting username (email or phone number)
        while True:
            if not options['email'] and not options['phone_number']:
                email = input('Enter email: ')
                phone_number = input('Enter phone number: ')
            else:
                email = options['email']
                phone_number = options['phone_number']

            # Basic input validation
            if not (email or phone_number):
                self.stdout.write(self.style.ERROR('Email or phone number required!'))
            elif email and not self.is_valid_email(email):
                self.stdout.write(self.style.ERROR('Invalid email format!'))
            elif phone_number and not self.is_valid_phone_number(phone_number):
                self.stdout.write(self.style.ERROR('Invalid phone number format!'))
            else:
                break

        # Collecting and validating password
        password = self.get_validated_password(options)

        try:
            # Creating superuser
            user = User.objects.create_superuser(email, phone_number, password)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser: {user.email or user.phone_number}'
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to create superuser: {str(e)}'))

    @classmethod
    def is_valid_email(cls, email):
        """
        This function checks if the provided email is a valid email address.
        """
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    @classmethod
    def is_valid_phone_number(cls, phone_number):
        """
        This function checks if the provided phone number is a valid phone number.
        """
        try:
            parsed_number = phonenumbers.parse(phone_number)
            if not phonenumbers.is_valid_number(parsed_number):
                return False
        except NumberParseException:
            return False
        return bool(phone_number)

    def get_validated_password(self, options: dict):
        """
        This function prompts the user to enter and confirm their password,
        then returns the confirmed password.
        """
        while True:
            if not options['password']:
                password = getpass('Enter password: ')

                # we need to change these arguments in production
                validator = CustomPasswordValidator(
                    min_length=0, require_digit=False, require_special_character=False
                )
                if not validator.is_valid(password):
                    self.stdout.write(self.style.ERROR('Password is too weak!'))
                    continue

                confirm_password = getpass('Retype password: ')

                if password != confirm_password:
                    self.stdout.write(self.style.ERROR('Passwords do not match!'))
                else:
                    return password
            else:
                return options['password']
