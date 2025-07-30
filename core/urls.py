from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from recognize_image.views import *

urlpatterns = [
    path("api/users/", include(("api.routers", "api"), namespace="api")),
    # path("api/video/", include("video.urls")),
    # path("api/music/", include("music.urls")),
    # path("api/event/", include("event.urls"))
    path("api/free-trial/", UserFreeTRailStausView.as_view()),
    path("api/recognize_image/", RecognizeImage.as_view()),
    path("api/user-history/", UserImagesHistoryView.as_view()),
    path("api/edit-history/", EditUserHistory.as_view()),
    path("api/delete-history/", DeleteUserHistory.as_view()),
    path("api/title-composer-update/", WriteTitleComposerView.as_view()),
    path('webhook/thrivecart/', ThriveCartWebhookView.as_view(), name='thrivecart-webhook'),
    path('api/payment-detail/', PaymentDetailView.as_view()),
    path('api/cancel-subscription/', CancelSubscriptionView.as_view()),



]

if settings.DEBUG == True or settings.DEBUG == False:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
