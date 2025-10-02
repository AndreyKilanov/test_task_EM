from enum import StrEnum

from django.utils.translation import gettext_lazy as _


class UserRole(StrEnum):

    ADMIN = 'admin'
    MODERATOR = 'moderator'
    CREATOR =  'creator'
    USER = 'user'

    def to_tuple(self):
        """
        Convert the enum member to a tuple suitable for choices.
        """
        return self.value, _(self.value.replace('_', ' ').title())
