from api.user.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "date",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "birthday",
            "school",
            "teacher",
            "software",
        ]
        read_only_field = ["id"]
