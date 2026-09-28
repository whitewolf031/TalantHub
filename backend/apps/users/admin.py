from django.contrib import admin

from .models import BotUser


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "telegram_id",
        "username",
        "first_name",
        "phone_number",
        "language",
        "is_blocked",
        "last_activity_at",
    )
    list_filter = ("language", "is_blocked")
    search_fields = ("telegram_id", "username", "first_name", "phone_number")
    readonly_fields = ("created_at", "updated_at", "last_activity_at")
    ordering = ("-created_at",)
