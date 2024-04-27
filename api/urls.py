from django.contrib import admin
from django.urls import path
from api.views import FileUploadView

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="file-upload"),
]