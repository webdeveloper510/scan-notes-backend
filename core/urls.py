from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from recognize_image.views import RecognizeImage

urlpatterns = [
    path("api/users/", include(("api.routers", "api"), namespace="api")),
    # path("api/video/", include("video.urls")),
    # path("api/music/", include("music.urls")),
    # path("api/event/", include("event.urls"))
    path("api/recognize_image/", RecognizeImage.as_view())
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
