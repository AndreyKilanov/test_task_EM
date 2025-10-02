import random
import string
from datetime import timedelta

from django.core.cache import cache

from users import constants


class ConfirmationCode:
    """
    Class for generating and validating confirmation codes for user registration.
    """
    CODE_LENGTH = constants.CODE_LENGTH
    CODE_EXPIRATION = timedelta(minutes=constants.CODE_EXPIRATION)

    @classmethod
    def generate_code(cls, email: str) -> str:
        """
        Generates a random confirmation code and stores it in the cache.
        :param email:           Email address to associate with the confirmation code.
        """
        code = ''.join(random.choices(string.digits, k=cls.CODE_LENGTH))
        cache.set(
            f'password_reset_{email}',
            code,
            timeout=int(cls.CODE_EXPIRATION.total_seconds())
        )
        return code

    @classmethod
    def validate_code(cls, email: str, code: str) -> bool:
        """ Validates the confirmation code against the cached value.
        :param email:           Email address associated with the confirmation code.
        :param code:            Confirmation code to validate.
        """
        cached_code = cache.get(f'password_reset_{email}')
        return cached_code == code

    @classmethod
    def delete_code(cls, email: str):
        """
        Delete used code.
        :param email:           Email address associated with the confirmation code.
        """
        cache_key = f'password_reset_{email}'
        cache.delete(cache_key)
