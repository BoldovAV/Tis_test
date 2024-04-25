from django.core.management import BaseCommand
from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options) -> None:
        user = User.objects.create(
            email='admin@ad.min',
            first_name='Admin',
            last_name='Adminskii',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )

        user.set_password('admin')
        user.save()
