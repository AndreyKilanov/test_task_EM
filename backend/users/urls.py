from django.urls import path
from rest_framework.routers import SimpleRouter

from users.apps import UsersConfig
from users.views import (
    LoginView,
    RegistrationView,
    RefreshTokenView,
    ChangePasswordView,
    PasswordRecoveryView,
    PasswordResetConfirmView,
    UserProfileViewSet,
)

app_name = UsersConfig.name

router = SimpleRouter()


urlpatterns = [
    path(
        'profile/',
         UserProfileViewSet.as_view(
             { 'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy' }
         ),
         name='user-profile'
    ),
    path('registration/', RegistrationView.as_view(), name="registration"),

    # JWT authentication
    path('auth/login/', LoginView.as_view(), name='auth_login'),
    path('auth/token-refresh/', RefreshTokenView.as_view(), name='token_refresh'),

    # Work with passwords
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/password-recovery/', PasswordRecoveryView.as_view(), name='password_recovery'),
    path(
        'auth/password-reset-confirm/',
        PasswordResetConfirmView.as_view(),
        name='reset_password_confirm'
    ),
]

urlpatterns += router.urls
