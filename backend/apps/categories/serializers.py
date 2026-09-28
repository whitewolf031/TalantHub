from rest_framework import serializers

from .models import AnnouncementCategory


class AnnouncementCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementCategory
        fields = ["id", "key", "emoji", "name_uz", "name_en", "name_ru", "order"]
