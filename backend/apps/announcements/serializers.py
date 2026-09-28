from rest_framework import serializers

from apps.categories.models import AnnouncementCategory
from apps.users.models import BotUser

from .models import Announcement
from .services import build_channel_text
from .validators import validate_contact_time_range


class AnnouncementCreateSerializer(serializers.ModelSerializer):
    telegram_id = serializers.IntegerField(write_only=True)
    category_key = serializers.SlugField(write_only=True)

    class Meta:
        model = Announcement
        fields = [
            "telegram_id",
            "category_key",
            "full_name",
            "age",
            "direction",
            "technologies",
            "telegram_username",
            "phone_number",
            "city_from",
            "city_looking",
            "salary_amount",
            "salary_currency",
            "contact_time_start",
            "contact_time_end",
            "purpose",
        ]

    def validate_age(self, value):
        if not (14 <= value <= 80):
            raise serializers.ValidationError("Yosh 14 dan 80 gacha bo'lishi kerak.")
        return value

    def validate(self, attrs):
        validate_contact_time_range(
            attrs.get("contact_time_start"), attrs.get("contact_time_end")
        )
        return attrs

    def create(self, validated_data):
        telegram_id = validated_data.pop("telegram_id")
        category_key = validated_data.pop("category_key")

        try:
            user = BotUser.objects.get(telegram_id=telegram_id)
        except BotUser.DoesNotExist:
            raise serializers.ValidationError(
                {"telegram_id": "Foydalanuvchi topilmadi. Avval /start bosing."}
            )

        try:
            category = AnnouncementCategory.objects.get(key=category_key, is_active=True)
        except AnnouncementCategory.DoesNotExist:
            raise serializers.ValidationError({"category_key": "Kategoriya topilmadi."})

        return Announcement.objects.create(
            user=user, category=category, **validated_data
        )


class AnnouncementReadSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.display_title", read_only=True)
    salary_display = serializers.CharField(read_only=True)
    contact_time_display = serializers.CharField(read_only=True)
    preview_text = serializers.SerializerMethodField()

    def get_preview_text(self, obj):
        return build_channel_text(obj)

    class Meta:
        model = Announcement
        fields = [
            "id",
            "category",
            "full_name",
            "age",
            "direction",
            "technologies",
            "telegram_username",
            "phone_number",
            "city_from",
            "city_looking",
            "salary_amount",
            "salary_currency",
            "salary_display",
            "contact_time_start",
            "contact_time_end",
            "contact_time_display",
            "purpose",
            "status",
            "preview_text",
            "created_at",
            "approved_at",
        ]
