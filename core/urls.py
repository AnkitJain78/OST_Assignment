from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from api.views import health_check

schema_view = get_schema_view(
    openapi.Info(
        title="CV Processing API",
        default_version="v1",
        description="An API for processing CVs, extracting email IDs, contact numbers, and overall text.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@cvprocessing.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", health_check),
    path("api/v1/", include("api.urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
