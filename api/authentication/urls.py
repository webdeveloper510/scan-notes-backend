from django.urls import path, include
from .views import GetProfileView

urlpatterns = [
    path("me", GetProfileView.as_view()),
]
