from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from users.entities import DesignTheme
from users.models.custom_user_model import CustomUser


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'middle_name', 'last_name', 'role', 'avatar', 'theme')


class UserProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    middle_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    avatar = serializers.CharField(
        required=False,
        allow_null=True,
        write_only=True
    )
    theme = serializers.ChoiceField(
        choices=DesignTheme,
        required=False
    )
    remove_avatar = serializers.BooleanField(
        default=False,
        required=False
    )

    class Meta:
        fields = ('first_name', 'last_name', 'middle_name', 'theme', 'remove_avatar', 'avatar')

    def validate(self, data):
        if data.get('avatar') and data.get('remove_avatar'):
            raise serializers.ValidationError(_("Cannot set both avatar and remove_avatar"))
        return data
