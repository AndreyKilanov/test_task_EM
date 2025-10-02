from enum import StrEnum

from django.utils.translation import gettext_lazy as _


class DesignTheme(StrEnum):

    LIGHT = 'light'
    DARK = 'dark'

    def to_tuple(self):
        """
        Convert the enum member to a tuple suitable for choices.
        """
        return self.value, _(self.value.title())
