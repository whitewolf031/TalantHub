from django.db import models


class Language(models.TextChoices):
    UZ = "uz", "O'zbekcha"
    EN = "en", "English"
    RU = "ru", "Русский"


class BotUser(models.Model):
    """Telegram bot orqali /start bosgan har bir foydalanuvchi."""

    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    language = models.CharField(
        max_length=2, choices=Language.choices, default=Language.UZ
    )
    is_blocked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name or 'NoName'} (@{self.username or '—'}) [{self.telegram_id}]"

    def last_approved_announcement(self):
        return (
            self.announcements.filter(status="approved")
            .order_by("-approved_at")
            .first()
        )
