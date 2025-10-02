from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from users.permissions import DynamicRolePermission

GROUP_NAME = "Resources | Dynamic Role Permission"


@extend_schema(
    tags=[GROUP_NAME],
    summary="List or create documents",
    description="Mock endpoint for documents. Requires 'read' permission for GET, 'write' for POST.",
    methods=["GET"],
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "string"},
                    "owner": {"type": "string"}
                },
                "required": ["id", "title", "owner"]
            }
        }
    },
)
@extend_schema(
    tags=[GROUP_NAME],
    summary="Create a new document",
    description="Mock endpoint to create a document. Requires 'write' permission.",
    methods=["POST"],
    request={"application/json": {"type": "object", "properties": {}, "example": {}}},
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "Document created"},
                "id": {"type": "integer", "example": 3}
            },
            "required": ["message", "id"]
        }
    },
)
@api_view(['GET', 'POST'])
@permission_classes([DynamicRolePermission])
def documents_view(request):
    """Mock endpoint for documents."""
    if request.method == 'GET':
        return Response([
            {"id": 1, "title": "Lease Agreement", "owner": "Ivan Ivanov"},
            {"id": 2, "title": "Invoice", "owner": "LLC Romashka"},
        ])
    elif request.method == 'POST':
        return Response(
            {"message": "Document created", "id": 3},
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    tags=[GROUP_NAME],
    summary="List reports",
    description="Mock endpoint for reports. Requires 'read' permission.",
    methods=["GET"],
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "date": {"type": "string", "format": "date"}
                },
                "required": ["id", "name", "date"]
            }
        }
    },
)
@extend_schema(
    tags=[GROUP_NAME],
    summary="Delete a report",
    description="Mock endpoint to delete a report. Requires 'delete' permission.",
    methods=["DELETE"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "Report deleted"}
            },
            "required": ["message"]
        }
    },
)
@api_view(['GET', 'DELETE'])
@permission_classes([DynamicRolePermission])
def reports_view(request):
    """Mock endpoint for reports."""
    if request.method == 'GET':
        return Response([
            {"id": 1, "name": "Daily Report", "date": "2024-06-01"},
        ])
    elif request.method == 'DELETE':
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=[GROUP_NAME],
    summary="List managed users",
    description="Mock endpoint for user management (admin only). Requires 'manage' or 'read' permission on users resource.",
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "role": {"type": "string", "enum": ["admin", "moderator", "creator", "user"]}
                },
                "required": ["email", "role"]
            }
        }
    },
)
@api_view(['GET'])
@permission_classes([DynamicRolePermission])
def users_management_view(request):
    """Mock endpoint for user management (admin only)."""
    return Response([
        {"email": "user1@example.com", "role": "user"},
        {"email": "moder@example.com", "role": "moderator"},
    ])
