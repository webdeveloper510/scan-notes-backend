from django.db import models


# Password Reset Model token
class PasswordResetToken(models.Model):
    user = models.ForeignKey('api_user.User', on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
