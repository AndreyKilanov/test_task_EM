from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from users import constants
from users.entities import UserRole
from users.models.custom_user_model import CustomUser
from users.services.user_service import user_manager
from users.utils import ConfirmationCode
from users.validators import UserValidators


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        return token


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    pass


class PasswordRecoverySerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not user_manager.get_user_by_email(value):
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=constants.CODE_LENGTH)
    password = serializers.CharField(
        write_only=True,
        validators=[UserValidators.validate_password,]
    )
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if not ConfirmationCode.validate_code(attrs['email'], attrs['code']):
            raise serializers.ValidationError(_("Invalid or expired code"))

        try:
            user = user_manager.get_user_by_email(attrs["email"])
            if user.check_password(attrs['password']):
                raise serializers.ValidationError(
                    _("New password cannot be the same as old password")
                )
        except CustomUser.DoesNotExist:
            return serializers.ValidationError(_("User with this email does not exist"))

        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(_("Passwords do not match"))

        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[UserValidators.validate_password,]
    )
    password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if not self.context['request'].user.check_password(attrs['old_password']):
            raise serializers.ValidationError(_("Incorrect password"))

        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError(_("New password cannot be the same as old password"))

        if attrs['new_password'] != attrs['password_confirm']:
            raise serializers.ValidationError(_("Passwords do not match"))
        return attrs


class UserRegistrationSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField([UserRole.USER, UserRole.CREATOR])
    password = serializers.CharField(
        write_only=True,
        validators=[UserValidators.validate_password,]
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'email', 'first_name', 'middle_name', 'last_name', 'role', 'password', 'password_confirm'
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(_("Password do not match"))
        if attrs['role'] not in [UserRole.USER, UserRole.CREATOR]:
            raise serializers.ValidationError(_("Invalid role"))
        return attrs
