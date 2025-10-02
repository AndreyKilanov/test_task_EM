import base64
from io import BytesIO

from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from users import constants


class AvatarHandler:
    """
    Class for handling avatars: loading via base64, checking the format and returning the file.
    """
    MAX_SIZE = constants.AVATAR_MAX_SIZE
    QUALITY = constants.AVATAR_QUALITY

    @classmethod
    def decode_avatar(cls, avatar_b64: str, email: str) -> ContentFile:
        """
        Decodes an avatar from a base64 string, resizes it, and returns as ContentFile.

        :param avatar_b64:      Base64 encoded image string.
        :param email:           Email address of the user to retrieve
        """
        try:
            img_format, img_str = avatar_b64.split(';base64,')
            ext = img_format.split('/')[-1]
            decoded_file = base64.b64decode(img_str)
            image = Image.open(BytesIO(decoded_file))

            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            image.thumbnail(cls.MAX_SIZE, Image.Resampling.LANCZOS)
            buffer = BytesIO()
            image.save(buffer, format=image.format, quality=cls.QUALITY)
            resized_image = buffer.getvalue()

            return ContentFile(resized_image, name=f'{email}.{ext}')

        except Exception as e:
            raise ValidationError(f"Error decoding or resizing file: {e}")

    @classmethod
    def validate_avatar(cls, avatar_b64: str):
        """
        Checks if a base64 string is a valid image and can be opened by PIL.

        :param avatar_b64:      Base64 encoded image string.
        """
        try:
            _, img_str = avatar_b64.split(';base64,')
            decoded_file = base64.b64decode(img_str)
            image = Image.open(BytesIO(decoded_file))
            image.verify()
        except Exception:
            raise ValidationError("Invalid avatar format. Base64 image expected.")

    @classmethod
    def get_avatar(cls, avatar_b64: str, email: str) -> ContentFile | None:
        """
        Returns a ContentFile of the avatar. If the avatar is not provided,
        returns None.

        :param avatar_b64:      Base64 encoded image string.
        :param email:           Email address of the user to retrieve.
        """
        if not avatar_b64:
            return None

        cls.validate_avatar(avatar_b64)
        return cls.decode_avatar(avatar_b64, email)
