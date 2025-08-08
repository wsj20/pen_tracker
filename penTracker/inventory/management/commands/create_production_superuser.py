import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a superuser for production from environment variables.'

    def handle(self, *args, **options):
        username = os.environ.get('SUPERUSER_NAME')
        email = os.environ.get('SUPERUSER_EMAIL')
        password = os.environ.get('SUPERUSER_PASSWORD')

        if not User.objects.filter(username=username).exists():
            print(f'Creating superuser: {username}')
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
        else:
            print(f'Superuser "{username}" already exists.')