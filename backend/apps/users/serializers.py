from rest_framework import serializers

from .models import BotUser


class BotUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotUser
        fields = [
            "id",
            "telegram_id",
            "username",
            "first_name",
            "phone_number",
            "language",
            "is_blocked",
            "created_at",
            "updated_at",
            "last_activity_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "last_activity_at"]


class BotUserRegisterSerializer(serializers.ModelSerializer):
    """/start bosilganda foydalanuvchini yaratish yoki yangilash uchun."""

    class Meta:
        model = BotUser
        fields = ["telegram_id", "username", "first_name", "language"]

    def create(self, validated_data):
        telegram_id = validated_data.pop("telegram_id")
        user, _created = BotUser.objects.update_or_create(
            telegram_id=telegram_id,
            defaults=validated_data,
        )
        return user
