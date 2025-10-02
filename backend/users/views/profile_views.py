from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets, status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from users.serializers import UserProfileUpdateSerializer, UserProfileSerializer
from users.services.user_service import user_manager


@extend_schema(tags=[_("Users")])
@extend_schema_view(
    retrieve=extend_schema(
        summary=_("Get Current User Profile | Authenticated User Only"),
        description=_("Get profile information for currently authenticated user"),
        responses={200: UserProfileSerializer}
    ),
    partial_update=extend_schema(
        summary=_("Update Current User Profile | Authenticated User Only"),
        description=_("Update profile information for currently authenticated user"),
        request=UserProfileUpdateSerializer,
        responses={200: UserProfileSerializer}
    ),
    destroy=extend_schema(
        summary=_("Delete Current User Profile | Authenticated User Only"),
        description=_("Deactivate the currently authenticated user account"),
        responses={204: None, 400: {"type": "object", "properties": {"error": {"type": "string"}}}}
    )
)
class UserProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UserProfileUpdateSerializer
        return UserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            updated_user = user_manager.update_user(user=request.user, **serializer.validated_data)
            response_data = UserProfileSerializer(updated_user, context={'request': request})

            return Response(response_data.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            user = request.user
            user_manager.delete_user(user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
