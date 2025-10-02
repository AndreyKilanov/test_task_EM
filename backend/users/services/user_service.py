import os

from django.core.exceptions import ValidationError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from users.constants import DEFAULT_AVATAR_NAME, DEFAULT_AVATAR_PATH
from users.utils import AvatarHandler

from users.entities import DesignTheme, UserRole
from users.models.custom_user_model import CustomUser


class UserManager:
    """
    Service class for managing users.
    """

    def __init__(self, user_model=None):
        self.user_model = user_model or CustomUser

    def get_user_by_email(self, email: str) -> CustomUser | None:
        """
        Retrieves a user by their email address.

        :param email:   Email address of the user to retrieve
        :return:        User instance if found, otherwise None
        """
        try:
            return self.user_model.objects.get(email=email.lower())
        except self.user_model.DoesNotExist:
            return None

    def create_user(
            self,
            email: str,
            password: str,
            first_name: str,
            middle_name: str,
            last_name: str,
            role: UserRole = UserRole.USER,
            theme: DesignTheme = DesignTheme.LIGHT,
            avatar: str | None = None,
    ) -> CustomUser:
        """
        Creates a new user with the provided details.

        :param email:           Email address of the user to create
        :param password:        Password for the user
        :param first_name:      First name of the user
        :param middle_name:     Middle name of the user
        :param last_name:       Last name of the user
        :param role:            Role of the user (default is USER)
        :param theme:           Design theme for the user (default is LIGHT)
        :param avatar:          Avatar base64 of the user (optional)
        :return:                The created user instance
        """
        email = email.lower()
        if self.user_model.objects.filter(email=email).exists():
            raise ValidationError(f"User with email {email} already exists.")

        valid_roles = UserRole
        if role not in valid_roles:
            raise ValidationError(f"Invalid role: {role}")

        avatar_file = None
        if avatar:
            try:
                avatar_file = AvatarHandler.get_avatar(avatar, email)
            except ValidationError as e:
                raise ValidationError(f"Invalid avatar: {str(e)}")

        user = self.user_model.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            role=role,
            theme=theme,
            avatar=avatar_file,
        )
        return user

    def update_user(
            self,
            user: CustomUser,
            *,
            email: str | None = None,
            first_name: str | None = None,
            middle_name: str | None = None,
            last_name: str | None = None,
            role: str | None = None,
            theme: DesignTheme | None = None,
            is_active: bool | None = None,
            avatar: str | None = None,
            remove_avatar: bool = False,
    ) -> CustomUser:
        """
        Updates the user's details.

        :param user:            The user instance to update
        :param email:           New email address for the user (optional)
        :param first_name:      New first name for the user (optional)
        :param middle_name:     New middle name for the user (optional)
        :param last_name:       New last name for the user (optional)
        :param role:            New role for the user (optional)
        :param theme:           New design theme for the user (optional)
        :param is_active:       Whether the user should be active (optional)
        :param avatar:          Avatar base64 of the user (optional)
        :param remove_avatar:   Whether the user should remove the avatar (optional)
        :return:                Updated user instance
        """
        email = email.lower()

        if email and email != user.email:
            if self.user_model.objects.filter(email=email).exists():
                raise ValidationError(f"User with email {email} already exists.")
            user.email = email

        if remove_avatar:
            if not user.avatar:
                raise ValidationError("User does not have an avatar to remove.")

            if os.path.basename(str(user.avatar)) == DEFAULT_AVATAR_NAME:
                raise ValidationError("Cannot remove default avatar.")

            user.avatar.delete(save=False)
            user.avatar = DEFAULT_AVATAR_PATH

        elif avatar:
            try:
                new_avatar = AvatarHandler.get_avatar(avatar, user.email)
                if user.avatar and os.path.basename(str(user.avatar)) != DEFAULT_AVATAR_NAME:
                    user.avatar.delete(save=False)
                user.avatar = new_avatar
            except ValidationError as e:
                raise ValidationError(f"Invalid avatar: {str(e)}")

        simple_fields = dict(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            role=role,
            theme=theme,
            is_active=is_active,
        )

        for field, value in simple_fields.items():
            if value is not None:
                setattr(user, field, value)

        user.save()
        return user

    def delete_user(self, user: CustomUser) -> None:
        """
        Delete the user.

        :param user:    The user instance to delete
        """

        if user.is_superuser:
            raise PermissionError("Cannot delete a superuser.")

        if user.is_archived:
            raise ValidationError(f"User {user.email} is already delete.")

        user.archive()

        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for token in outstanding_tokens:
            BlacklistedToken.objects.get_or_create(token=token)


user_manager = UserManager()
