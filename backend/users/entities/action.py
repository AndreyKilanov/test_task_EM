from enum import StrEnum
from django.utils.translation import gettext_lazy as _


class Action(StrEnum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    MANAGE = "manage"

    @classmethod
    def choices(cls):
        return [
            (cls.READ, _('Read')),
            (cls.WRITE, _('Write')),
            (cls.DELETE, _('Delete')),
            (cls.MANAGE, _('Full access')),
        ]
