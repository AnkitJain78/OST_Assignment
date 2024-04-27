from django.contrib import admin
from api.models import File


class FileAdmin(admin.ModelAdmin):
    model = File
    fields = ["__all__"]


admin.site.register(File, FileAdmin)
