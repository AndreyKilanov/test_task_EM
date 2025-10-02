from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users import constants
from users.entities import UserRole, DesignTheme
from users.models.managers import CustomUserManager
from users.validators import UserValidators

USER_ROLE_CHOICES = tuple(role.to_tuple() for role in UserRole)
DESIGN_THEME_CHOICES = tuple(theme.to_tuple() for theme in DesignTheme)


class CustomUser(AbstractUser):
    """
    Custom user model.
    This model extends the default Django user model to include additional fields.
    """
    username = None
    email = models.EmailField(
        unique=True,
        validators=(MaxLengthValidator(constants.EMAIL_MAX_LENGTH),),
        verbose_name=_('email'),
    )
    first_name = models.CharField(
        max_length=constants.FIRST_NAME_MAX_LENGTH,
        validators=(
            UserValidators.validate_first_name,
            MinLengthValidator(constants.FIRST_NAME_MIN_LENGTH),
        ),
        verbose_name=_('first name'),
    )
    middle_name = models.CharField(
        max_length=constants.MIDDLE_NAME_MAX_LENGTH,
        validators=(
            UserValidators.validate_middle_name,
            MinLengthValidator(constants.MIDDLE_NAME_MIN_LENGTH),
        ),
        verbose_name=_('middle name'),
    )
    last_name = models.CharField(
        max_length=constants.LAST_NAME_MAX_LENGTH,
        verbose_name=_('last name'),
        validators=(
            UserValidators.validate_last_name,
            MinLengthValidator(constants.LAST_NAME_MIN_LENGTH),
        ),
    )
    avatar = models.ImageField(
        upload_to=constants.AVATAR_PATH,
        blank=True,
        verbose_name=_('avatar'),
    )
    role = models.CharField(
        max_length=constants.CHARFIELD_MAX_LENGTH,
        choices=USER_ROLE_CHOICES,
        default=UserRole.USER,
        verbose_name=_('role'),
    )
    theme = models.CharField(
        max_length=constants.CHARFIELD_MAX_LENGTH,
        choices=DESIGN_THEME_CHOICES,
        default=DesignTheme.LIGHT,
        verbose_name=_('design theme'),
    )
    password_changed_at = models.DateField(
        default=timezone.now,
        verbose_name=_('password changed at'),
    )
    is_archived = models.BooleanField(
        default=False,
        verbose_name=_('is archived'),
    )
    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('archived at')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'

    def save(self, *args, **kwargs):
        """
        Override the save method to set a default avatar if none is provided.
        """
        if not self.avatar:
            self.avatar = constants.DEFAULT_AVATAR_PATH
        super().save(*args, **kwargs)

    def archive(self):
        """
        Marks the user as archived and sets the archived_at timestamp.
        """
        self.is_archived = True
        self.archived_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['is_archived', 'archived_at', 'is_active'])
