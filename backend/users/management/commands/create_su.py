import os
from pathlib import Path

from django.core.management.base import BaseCommand

from users.models.custom_user_model import CustomUser

PATH_DEFAULT_AVATAR = os.path.join(Path(__file__).parent.parent, "data")


class Command(BaseCommand):
    help = (
        'Creates a superuser using environment variables ADMIN_EMAIL and'
        ' ADMIN_PASSWORD if not exists and assigns default avatar.'
    )

    def handle(self, *args, **options):
        email = os.getenv('ADMIN_EMAIL')
        password = os.getenv('ADMIN_PASSWORD')

        if not email or not password:
            self.stderr.write("Error: ADMIN_EMAIL and ADMIN_PASSWORD must be set in .env")
            return

        if CustomUser.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'Superuser with email "{email}" already exists. Skipping creation.'
                )
            )
            return

        try:
            default_avatar_path = os.path.join(PATH_DEFAULT_AVATAR, 'default_avatar.png')
            media_avatar_path = os.path.join('media', 'users', 'avatars', 'default_avatar.png')

            os.makedirs(os.path.dirname(media_avatar_path), exist_ok=True)

            if not os.path.exists(media_avatar_path):
                with open(default_avatar_path, 'rb') as src, open(media_avatar_path, 'wb') as dst:
                    dst.write(src.read())

            user = CustomUser.objects.create_superuser(email=email, password=password)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Superuser {user.email} created successfully with default avatar.'
                )
            )

        except Exception as e:
            self.stderr.write(f'Error: {str(e)}')
