from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import ProgrammingError, OperationalError
import os

class Command(BaseCommand):
    help = 'Creates a superuser if none exists'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        try:
            if not User.objects.filter(is_superuser=True).exists():
                username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
                email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
                password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')
                first_name = os.environ.get('DJANGO_SUPERUSER_FIRSTNAME', 'Admin')
                last_name = os.environ.get('DJANGO_SUPERUSER_LASTNAME', 'User')

                self.stdout.write('Creating superuser account...')

                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )

                user.is_active = True
                user.is_admin = True
                user.is_staff = True
                user.save()

                self.stdout.write(self.style.SUCCESS('Superuser account created successfully'))
            else:
                self.stdout.write('Superuser account already exists')

        except (ProgrammingError, OperationalError) as e:
            self.stdout.write(self.style.WARNING(
                f"Skipping superuser creation: Database table not ready yet. Error: {str(e)}"
            ))