from api.user.models import User , CropImageHistoryModel
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
            "file_upload_count"
        ]
        read_only_field = ["id"]


class EditUserHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CropImageHistoryModel
        fields = '__all__'
