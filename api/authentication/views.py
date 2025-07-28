from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.user.serializers import UserSerializer
from api.user.models import User
from api.authentication.models.password_reset import PasswordResetToken
from api.user.models import ContactSupportModel
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.contrib.auth.hashers import make_password
import sys
from api.authentication.utils import send_reset_password_email , send_contact_support_email



class GetProfileView(views.APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):

        user = UserSerializer(request.user)

        return Response({"success": True, "user": user.data}, status.HTTP_200_OK)

# API for Send password Reset Request
class PasswordResetRequestView(views.APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        try:

            #email  = request.data.get("email")
            email  = request.user.email
            print("email ",email)


            if not email:
                return Response({'error': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.get(email=email)  # fetch the user from DB
            if not user:
                return Response({'error': 'Email not found'}, status=404)
            
            print("user ",user)
            token = get_random_string(64)

            PasswordResetToken.objects.create(user=user, token=token, expires_at=timezone.now() + timezone.timedelta(hours=1))

            reset_url = f"https://fichedetravail.com/reset-password/{token}/"
            
            #reset_url = f"http://127.0.0.1:8000/api/users/reset-password/{token}/"

            email_status= send_reset_password_email(email, reset_url)
            if not email_status:
                return Response({"success": email_status, "message": "Failed to send Reset Link"}, status.HTTP_400_BAD_REQUEST)
            return Response({"success": email_status, "message": "Reset link sent"}, status.HTTP_200_OK)
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = f"{str(e)} in line {exc_tb.tb_lineno}"
            return Response({"success": False, "message":error_message }, status.HTTP_500_INTERNAL_SERVER_ERROR)


# APi for Reset password 
class ResetPassword(views.APIView):
    #permission_classes = (IsAuthenticated)

    def post(self, request, token):
        try:
            
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')


            if new_password != confirm_password:
                return Response({"success": False, "message":"New password and confirm password does not matched" }, status.HTTP_406_NOT_ACCEPTABLE)
            
            reset_obj = PasswordResetToken.objects.filter(token=token).first()
            if not reset_obj or reset_obj.expires_at < timezone.now():
                return Response({'error': 'Invalid or expired token'}, status=400)

            user = reset_obj.user

            user.password = make_password(new_password)
            user.save()
            reset_obj.delete()  # Invalidate token

            return Response({"success": True, 'message': 'Password reset successful'}, status=status.HTTP_200_OK)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = f"{str(e)} in line {exc_tb.tb_lineno}"
            return Response({"success": False, "message":error_message }, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
# APi for Contact Support
class ContactSupportView(views.APIView):
    #permission_classes = (IsAuthenticated)

    def post(self, request , format=None):
        try:
            
            payload = request.data

            required_fields = ["first_name", "last_name", "email", "reason", "message"]

            missing_fields = [field for field in required_fields if not payload.get(field)]

            if missing_fields:
                return Response(
                    {"success": False, "message": f"{', '.join(missing_fields)} key is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create in database
            ContactSupportModel.objects.create(
                first_name=payload.get("first_name"),
                last_name=payload.get("last_name"),
                email=payload.get("email"),
                reason=payload.get("reason"),
                message=payload.get("message")
            )

            contact_email_message = send_contact_support_email(payload)

            if not contact_email_message:
                return Response({"success": contact_email_message, "message": "Failed to send contact support email"}, status.HTTP_400_BAD_REQUEST)
            return Response({"success": contact_email_message, "message": "contact support email send succesfully"}, status.HTTP_200_OK)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = f"{str(e)} in line {exc_tb.tb_lineno}"
            return Response({"success": False, "message":error_message }, status.HTTP_500_INTERNAL_SERVER_ERROR)
        