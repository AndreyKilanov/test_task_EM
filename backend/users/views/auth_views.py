from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, permissions, generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users import constants
from users.serializers import (
    UserRegistrationSerializer,
    PasswordResetConfirmSerializer,
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    ChangePasswordSerializer,
    PasswordRecoverySerializer,
    UserProfileSerializer,
)
from users.services.user_service import user_manager
from users.utils import ConfirmationCode

DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL or "abc@gmail.com"


@extend_schema(
    tags=[_("Users")],
    summary=_("User Login | Allow Any"),
    description=_("Authenticate user and receive JWT tokens."),
    request=CustomTokenObtainPairSerializer,
)
class LoginView(TokenObtainPairView):
    """
    View to handle user login and token generation.
    """
    http_method_names = ["post"]
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    tags=[_("Users")],
    summary=_("Token Refresh"),
    description=_("Refresh JWT tokens using a valid refresh token."),
    request=CustomTokenRefreshSerializer,
)
class RefreshTokenView(TokenRefreshView):
    """
    View to handle token refresh.
    """
    http_method_names = ["post"]
    serializer_class = CustomTokenRefreshSerializer


@extend_schema(
    tags=[_("Users")],
    summary=_("Change Password | Authenticated User Only"),
    description=_("Change the password for an authenticated user."),
    request=ChangePasswordSerializer
)
class ChangePasswordView(generics.GenericAPIView):
    """
    View to handle password change for authenticated users.
    """
    http_method_names = ["post"]
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {"old_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"detail": "Password updated successfully"})


@extend_schema(
    tags=[_("Users")],
    summary=_("Password Recovery | Allow Any"),
    description=_("Send a password reset code to the user's email."),
    request=PasswordRecoverySerializer
)
class PasswordRecoveryView(generics.GenericAPIView):
    """
    View to handle password recovery by sending a reset code to the user's email.
    """
    http_method_names = ["post"]
    serializer_class = PasswordRecoverySerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data['email']
            user_manager.get_user_by_email(email=email)

            code = ConfirmationCode.generate_code(email)

            # Uncomment the following line to send the email with the reset code
            # send_mail(
            #     'Password Reset Code',
            #     f'Your password reset code is: {code}',
            #     DEFAULT_FROM_EMAIL,
            #     [email],
            #     fail_silently=False,
            # )

            return Response(
                {
                    "detail": f"Reset code sent to email: {email}",
                    "email": email,
                    "code": code,  # This is for testing purposes, remove in production
                    "expires_in": f"{constants.CODE_EXPIRATION} minutes"
                }, status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(
    tags=[_("Users")],
    summary=_("Password Reset Confirmation | Allow Any"),
    description=_("Reset the user's password using the reset code sent to their email."),
    request=PasswordResetConfirmSerializer
)
class PasswordResetConfirmView(generics.GenericAPIView):
    http_method_names = ["post"]
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data['email']
            new_password = serializer.validated_data['password']

            user = user_manager.get_user_by_email(email=email)
            user.set_password(new_password)
            user.save()
            ConfirmationCode.delete_code(email)

            return Response({"detail": "Password has been reset successfully"})

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=[_("Users")],
    summary=_("Registrations new User | Allow Any"),
    description=_("Create a new user in the system."),
    request=UserRegistrationSerializer
)
class RegistrationView(generics.GenericAPIView):
    http_method_names = ['post']
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=UserRegistrationSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_data = serializer.validated_data
        user_data.pop('password_confirm', None)

        try:
            user = user_manager.create_user(**user_data)
            profile = UserProfileSerializer(user, context={'request': request})

            return Response(profile.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
