from django.contrib import admin

from .models import BotUser, Referral, ReferralCampaign


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "telegram_id",
        "username",
        "first_name",
        "phone_number",
        "language",
        "free_premium_posts",
        "is_blocked",
        "last_activity_at",
    )
    list_filter = ("language", "is_blocked")
    search_fields = ("telegram_id", "username", "first_name", "phone_number")
    readonly_fields = ("created_at", "updated_at", "last_activity_at")
    ordering = ("-created_at",)


@admin.register(ReferralCampaign)
class ReferralCampaignAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "code",
        "invited_count",
        "target_count",
        "is_active",
        "is_rewarded",
        "created_at",
        "expires_at",
    )
    list_filter = ("is_active", "is_rewarded")
    search_fields = ("code", "user__telegram_id", "user__username", "user__first_name")
    readonly_fields = ("created_at",)


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("id", "inviter", "referred_user", "campaign", "created_at")
    search_fields = (
        "inviter__telegram_id",
        "inviter__username",
        "referred_user__telegram_id",
        "referred_user__username",
    )
    readonly_fields = ("created_at",)

