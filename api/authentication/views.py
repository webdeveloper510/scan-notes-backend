from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.user.serializers import UserSerializer


class GetProfileView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = UserSerializer(request.user)

        return Response({"success": True, "user": user.data}, status.HTTP_200_OK)
