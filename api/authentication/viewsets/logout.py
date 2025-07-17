from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from api.authentication.models import ActiveSession


class LogoutViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            sessions = ActiveSession.objects.filter(user=user)
            for session in sessions:
                session.delete()
        except ObjectDoesNotExist:
            return Response("No active session found", status=status.HTTP_404_NOT_FOUND)
        except MultipleObjectsReturned:
            # Handle the case where multiple active sessions exist
            # Choose one session to delete or delete all sessions

            # Your custom logic here

            return Response(
                "Multiple active sessions found",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"success": True, "msg": "Token revoked"}, status=status.HTTP_200_OK
        )
