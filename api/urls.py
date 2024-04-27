from django.contrib import admin
from django.urls import path
from api.views import FileUploadView, EmailView

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    path("email/", EmailView.as_view(), name="email-user"),
]
