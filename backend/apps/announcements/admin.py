from django.contrib import admin, messages

from .models import Announcement, AnnouncementStatus, PaymentSetting
from .services import approve_announcement, delete_resume, reject_announcement


@admin.register(PaymentSetting)
class PaymentSettingAdmin(admin.ModelAdmin):
    list_display = ("card_number", "card_owner", "amount", "is_active", "updated_at")
    list_editable = ("amount", "is_active")


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "category",
        "full_name",
        "is_premium",
        "post_count",
        "direction",
        "phone_number",
        "status",
        "created_at",
    )
    list_filter = ("status", "is_premium", "category", "salary_currency")
    search_fields = ("full_name", "phone_number", "telegram_username", "direction")
    # Status faqat "Tasdiqlash" / "Rad etish" amallari orqali o'zgaradi
    # (shunda kanalga yuborish va foydalanuvchiga xabar har doim ishlaydi).
    readonly_fields = (
        "user",
        "status",
        "post_count",
        "created_at",
        "updated_at",
        "approved_at",
        "rejected_at",
        "resume_deleted_at",
        "channel_message_id",
    )
    actions = ["approve_and_publish", "reject_selected", "delete_resumes"]
    ordering = ("-created_at",)

    @admin.action(description="✅ Tasdiqlash va kanalga yuborish")
    def approve_and_publish(self, request, queryset):
        published, failed = 0, 0
        for pk in queryset.filter(status=AnnouncementStatus.PENDING).values_list("pk", flat=True):
            _, code = approve_announcement(pk)
            if code == "ok":
                published += 1
            else:
                failed += 1

        if published:
            self.message_user(
                request,
                f"{published} ta e'lon tasdiqlandi va kanalga yuborildi.",
                level=messages.SUCCESS,
            )
        if failed:
            self.message_user(
                request,
                f"{failed} ta e'lon yuborilmadi. BOT_TOKEN / CHANNEL_ID sozlamalarini va "
                f"bot kanalda admin ekanligini tekshiring.",
                level=messages.ERROR,
            )
        if not published and not failed:
            self.message_user(request, "Kutilayotgan (pending) e'lon tanlanmadi.", level=messages.WARNING)

    @admin.action(description="❌ Rad etish")
    def reject_selected(self, request, queryset):
        rejected = 0
        for pk in queryset.filter(status=AnnouncementStatus.PENDING).values_list("pk", flat=True):
            _, code = reject_announcement(pk)
            if code == "ok":
                rejected += 1
        self.message_user(request, f"{rejected} ta e'lon rad etildi.", level=messages.INFO)

    @admin.action(description="🗑 Tanlangan e'lonlarning rezyumesini o'chirish")
    def delete_resumes(self, request, queryset):
        deleted = 0
        for pk in queryset.filter(resume_file__isnull=False).exclude(resume_file="").values_list("pk", flat=True):
            if delete_resume(pk):
                deleted += 1
        self.message_user(request, f"{deleted} ta rezyume fayli o'chirildi.", level=messages.INFO)

