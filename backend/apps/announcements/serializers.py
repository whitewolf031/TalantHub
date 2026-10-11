from rest_framework import serializers

from apps.categories.models import AnnouncementCategory
from apps.users.models import BotUser

from .models import Announcement, PaymentSetting
from .services import build_channel_text
from .validators import validate_contact_time_range

ALLOWED_RESUME_EXTENSIONS = (".pdf", ".doc", ".docx")
MAX_RESUME_SIZE = 2 * 1024 * 1024  # 2 MB


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
            "is_premium",
            "linkedin_url",
            "portfolio_url",
            "resume_file",
            "payment_receipt",
        ]

    def validate_age(self, value):
        if not (14 <= value <= 80):
            raise serializers.ValidationError("Yosh 14 dan 80 gacha bo'lishi kerak.")
        return value

    def validate_resume_file(self, value):
        if value:
            if value.size > MAX_RESUME_SIZE:
                raise serializers.ValidationError("Rezyume hajmi 2 MB dan oshmasligi kerak.")
            filename = value.name.lower()
            if not any(filename.endswith(ext) for ext in ALLOWED_RESUME_EXTENSIONS):
                raise serializers.ValidationError("Faqat PDF, DOC yoki DOCX formatdagi fayllar qabul qilinadi.")
        return value

    def validate(self, attrs):
        validate_contact_time_range(
            attrs.get("contact_time_start"), attrs.get("contact_time_end")
        )

        is_premium = attrs.get("is_premium", False)
        if is_premium:
            if not attrs.get("linkedin_url"):
                raise serializers.ValidationError({"linkedin_url": "Pullik e'londa LinkedIn havolasi kiritilishi shart."})
            if not attrs.get("resume_file"):
                raise serializers.ValidationError({"resume_file": "Pullik e'londa Rezyume fayli yuklanishi shart."})

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
    resume_file_url = serializers.SerializerMethodField()
    payment_receipt_url = serializers.SerializerMethodField()

    def get_preview_text(self, obj):
        return build_channel_text(obj)

    def get_resume_file_url(self, obj):
        if obj.resume_file:
            return obj.resume_file.url
        return None

    def get_payment_receipt_url(self, obj):
        if obj.payment_receipt:
            return obj.payment_receipt.url
        return None

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
            "is_premium",
            "linkedin_url",
            "portfolio_url",
            "resume_file",
            "resume_file_url",
            "payment_receipt",
            "payment_receipt_url",
            "post_count",
            "next_publish_date",
            "resume_deleted_at",
            "feedback_asked_at",
            "is_completed",
            "is_free_premium_reward",
            "status",
            "preview_text",
            "created_at",
            "approved_at",
        ]


class PaymentSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSetting
        fields = [
            "id",
            "card_number",
            "card_owner",
            "amount",
            "instruction_uz",
            "instruction_en",
            "instruction_ru",
            "is_active",
            "updated_at",
        ]

