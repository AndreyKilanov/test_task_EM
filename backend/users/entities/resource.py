from enum import StrEnum
from django.utils.translation import gettext_lazy as _


class Resource(StrEnum):
    DOCUMENTS = "api/v1/documents"
    REPORTS = "api/v1/reports"
    USERS = "api/v1/users"

    @classmethod
    def choices(cls):
        return [
            (cls.DOCUMENTS, _('Documents')),
            (cls.REPORTS, _('Reports')),
            (cls.USERS, _('Users')),
        ]
