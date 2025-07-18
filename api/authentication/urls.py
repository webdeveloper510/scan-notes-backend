from django.urls import path, include
from .views import GetProfileView , PasswordResetRequestView , ResetPassword , ContactSupportView


urlpatterns = [
    path("me", GetProfileView.as_view()),

    # new added
    path("reset-request", PasswordResetRequestView.as_view()),
    path('reset-password/<str:token>/', ResetPassword.as_view()),
    path('contact-support', ContactSupportView.as_view()),
]

