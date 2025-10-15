from django.urls import path
from .views import ALPRProcessView

urlpatterns = [
    path("alpr/", ALPRProcessView.as_view(), name="alpr-process"),
]
