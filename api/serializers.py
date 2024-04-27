from rest_framework.serializers import ModelSerializer, ValidationError
from api.models import File


class FileSerializer(ModelSerializer):
    class Meta:
        model = File
        fields = ["__all__"]

    def validate(self, data):
        file = data.get("file")
        if file.size > 1024 * 1024 * 2:
            raise ValidationError("File size should not exceed 2 MB")
        return data

    def create(self, validated_data):
        file = File.objects.create(**validated_data)
        return file
