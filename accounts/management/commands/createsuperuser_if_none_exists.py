import os
from django.core.management.base import BaseCommand
from accounts.models import Account


class Command(BaseCommand):
    help = "Create a superuser for the custom Account model (email login) using environment variables"

    def handle(self, *args, **kwargs):
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        full_name = os.getenv("DJANGO_SUPERUSER_FULLNAME")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        # Ensure all variables are present
        if not all([email, username, full_name, password]):
            self.stdout.write(
                self.style.ERROR(
                    "Missing one or more required environment variables: "
                    "DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_USERNAME, "
                    "DJANGO_SUPERUSER_FULLNAME, DJANGO_SUPERUSER_PASSWORD"
                )
            )
            return

        if Account.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"User with email {email} already exists."))
            return

        user = Account.objects.create_superuser(
            email=email,
            username=username,
            full_name=full_name,
            password=password,
        )
        user.is_active = True  # ensure admin can log in
        user.save()

        self.stdout.write(self.style.SUCCESS(f"Superuser {email} created successfully!"))
