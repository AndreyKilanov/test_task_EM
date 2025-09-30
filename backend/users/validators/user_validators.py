import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class UserValidators:
    @staticmethod
    def validate_password(value):
        """
        Validate that the password meets security requirements.

        The password must:
            - Contain only Latin letters (a–z, A–Z), digits (0–9), and allowed special characters:
            ``!@#$%^&*()_+-=[]{};':"|,.<>/?``

            - Include at least one lowercase letter, one uppercase letter, and one digit.

            - Exclude all non-Latin alphabetic characters (e.g., Cyrillic, accented letters, etc.).

        Raises:
            ValidationError: If the password fails any of the above criteria.
        """
        if re.search(r'[^\x00-\x7F]', value):
            raise ValidationError(
                _('Password must contain only Latin characters, digits and special symbols. '
                  'Cyrillic and other non-Latin alphabets are not allowed.')
            )

        allowed_chars = r'a-zA-Z0-9!@#$%^&*()_+-=\[\]{};\':"|,.<>\/?'

        if not re.fullmatch(f'^[{allowed_chars}]*$', value):
            raise ValidationError(
                _('Password contains invalid characters. '
                  'Allowed: Latin letters, digits and !@#$%^&*()_+-=[]{};\':"|,.<>/?')
            )

        errors = []
        if not re.search(r'[a-z]', value):
            errors.append(_('at least one lowercase letter'))
        if not re.search(r'[A-Z]', value):
            errors.append(_('at least one uppercase letter'))
        if not re.search(r'[0-9]', value):
            errors.append(_('at least one digit'))

        if errors:
            raise ValidationError(
                _('The password must contain: ') + ', '.join(errors)
            )

        if len(value) < 8:
            raise ValidationError(
                _('Password must be at least 8 characters long.')
            )

    @staticmethod
    def validate_name(value):
        """
        Name must:
            - Contain only Latin or Cyrillic letters, hyphens, and spaces.
            - Consist of no more than 2 words.
            - Have each word start with an uppercase letter (title case).
        """
        if not re.fullmatch(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', value):
            raise ValidationError(
                _('Must contain only Latin or Cyrillic letters, hyphen, and space.')
            )

        words = value.strip().split()
        if len(words) == 0:
            raise ValidationError(_('Field cannot be empty.'))
        if len(words) > 2:
            raise ValidationError(_('It must contain no more than 2 words.'))

        for word in words:
            if not word:
                continue
            if word != word.capitalize():
                raise ValidationError(
                    _('Each word must start with an uppercase letter followed by lowercase letters.')
                )

    @classmethod
    def validate_first_name(cls, value):
        """
        First name validator.
        """
        cls.validate_name(value)

    @classmethod
    def validate_middle_name(cls, value):
        """
        Middle name validator.
        """
        cls.validate_name(value)

    @classmethod
    def validate_last_name(cls, value):
        """
        Last name validator.
        """
        cls.validate_name(value)
