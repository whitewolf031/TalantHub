from django.utils import timezone
from rest_framework import serializers

from .models import BotUser, Referral, ReferralCampaign


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
            "free_premium_posts",
            "created_at",
            "updated_at",
            "last_activity_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "last_activity_at"]


class ReferralCampaignSerializer(serializers.ModelSerializer):
    invited_count = serializers.IntegerField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = ReferralCampaign
        fields = [
            "id",
            "code",
            "created_at",
            "expires_at",
            "is_active",
            "is_rewarded",
            "target_count",
            "invited_count",
            "is_expired",
        ]


class BotUserRegisterSerializer(serializers.ModelSerializer):
    """/start bosilganda foydalanuvchini yaratish yoki yangilash uchun."""
    ref_code = serializers.CharField(write_only=True, required=False, allow_blank=True, default="")

    class Meta:
        model = BotUser
        fields = ["telegram_id", "username", "first_name", "language", "ref_code"]

    def create(self, validated_data):
        ref_code = validated_data.pop("ref_code", "")
        telegram_id = validated_data.pop("telegram_id")

        existing_user = BotUser.objects.filter(telegram_id=telegram_id).first()
        is_new = existing_user is None

        user, _created = BotUser.objects.update_or_create(
            telegram_id=telegram_id,
            defaults=validated_data,
        )

        self.referral_event = None
        if is_new and ref_code:
            self._process_referral(user, ref_code)

        return user

    def _process_referral(self, new_user: BotUser, ref_code: str):
        campaign = (
            ReferralCampaign.objects.filter(code=ref_code, is_active=True)
            .select_related("user")
            .first()
        )
        if not campaign:
            return

        if timezone.now() > campaign.expires_at:
            campaign.is_active = False
            campaign.save(update_fields=["is_active"])
            return

        if campaign.user_id == new_user.id:
            return

        if Referral.objects.filter(referred_user=new_user).exists():
            return

        Referral.objects.create(
            campaign=campaign,
            inviter=campaign.user,
            referred_user=new_user,
        )

        count = campaign.referrals.count()
        rewarded = False
        if count >= campaign.target_count and not campaign.is_rewarded:
            campaign.is_rewarded = True
            campaign.is_active = False
            campaign.save(update_fields=["is_rewarded", "is_active"])
            campaign.user.free_premium_posts += 1
            campaign.user.save(update_fields=["free_premium_posts"])
            rewarded = True

        self.referral_event = {
            "inviter_telegram_id": campaign.user.telegram_id,
            "inviter_lang": campaign.user.language,
            "invited_count": count,
            "target_count": campaign.target_count,
            "rewarded": rewarded,
            "referred_name": new_user.first_name or "Do'stingiz",
        }

