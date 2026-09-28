from rest_framework import serializers

from apps.announcements.models import Announcement
from apps.announcements.validators import validate_contact_time_range
from apps.categories.models import AnnouncementCategory
from apps.users.models import BotUser


class CategoryBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementCategory
        fields = ["id", "key", "emoji", "name_uz", "name_en", "name_ru"]


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotUser
        fields = ["id", "telegram_id", "username", "first_name", "language", "is_blocked"]


class AdminCategorySerializer(serializers.ModelSerializer):
    announcements_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = AnnouncementCategory
        fields = [
            "id", "key", "emoji", "name_uz", "name_en", "name_ru",
            "is_active", "order", "announcements_count",
        ]


class AdminBotUserSerializer(serializers.ModelSerializer):
    announcements_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = BotUser
        fields = [
            "id", "telegram_id", "username", "first_name", "phone_number",
            "language", "is_blocked", "created_at", "last_activity_at",
            "announcements_count",
        ]
        read_only_fields = ["id", "telegram_id", "created_at", "last_activity_at"]


class AdminAnnouncementSerializer(serializers.ModelSerializer):
    """Ro'yxat va batafsil ko'rish uchun (o'qish)."""

    category = CategoryBriefSerializer(read_only=True)
    user = UserBriefSerializer(read_only=True)
    salary_display = serializers.CharField(read_only=True)
    contact_time_display = serializers.CharField(read_only=True)

    class Meta:
        model = Announcement
        fields = [
            "id", "category", "user", "full_name", "age", "direction",
            "technologies", "telegram_username", "phone_number", "city_from",
            "city_looking", "salary_amount", "salary_currency", "salary_display",
            "contact_time_start", "contact_time_end", "contact_time_display",
            "purpose", "status", "reject_reason", "channel_message_id",
            "created_at", "approved_at", "rejected_at",
        ]


class AdminAnnouncementWriteSerializer(serializers.ModelSerializer):
    """Adminning e'lonni tahrirlashi uchun (status faqat approve/reject orqali o'zgaradi)."""

    category = serializers.PrimaryKeyRelatedField(queryset=AnnouncementCategory.objects.all())

    class Meta:
        model = Announcement
        fields = [
            "category", "full_name", "age", "direction", "technologies",
            "telegram_username", "phone_number", "city_from", "city_looking",
            "salary_amount", "salary_currency", "contact_time_start",
            "contact_time_end", "purpose",
        ]

    def validate_age(self, value):
        if not (14 <= value <= 80):
            raise serializers.ValidationError("Yosh 14 dan 80 gacha bo'lishi kerak.")
        return value

    def validate(self, attrs):
        start = attrs.get("contact_time_start", getattr(self.instance, "contact_time_start", None))
        end = attrs.get("contact_time_end", getattr(self.instance, "contact_time_end", None))
        try:
            validate_contact_time_range(start, end)
        except Exception as exc:  # django ValidationError -> DRF
            raise serializers.ValidationError({"contact_time_end": exc.messages})
        return attrs
