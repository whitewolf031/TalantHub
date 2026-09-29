from django.db import models

from apps.categories.models import AnnouncementCategory
from apps.users.models import BotUser

from .validators import (
    validate_full_name,
    validate_phone_number,
    validate_telegram_username,
)


class Currency(models.TextChoices):
    UZS = "UZS", "so'm"
    USD = "USD", "USD"


class AnnouncementStatus(models.TextChoices):
    PENDING = "pending", "Kutilmoqda"
    APPROVED = "approved", "Tasdiqlangan"
    REJECTED = "rejected", "Rad etilgan"


class Announcement(models.Model):
    user = models.ForeignKey(
        BotUser, on_delete=models.CASCADE, related_name="announcements"
    )
    category = models.ForeignKey(
        AnnouncementCategory, on_delete=models.PROTECT, related_name="announcements"
    )

    full_name = models.CharField(max_length=100, validators=[validate_full_name])
    age = models.PositiveSmallIntegerField()
    direction = models.CharField(max_length=150, verbose_name="Yo'nalish")
    technologies = models.CharField(
        max_length=1000,
        verbose_name="Texnologiyalar"
    )
    
    telegram_username = models.CharField(
        max_length=33, validators=[validate_telegram_username]
    )
    phone_number = models.CharField(max_length=20, validators=[validate_phone_number])

    city_from = models.CharField(max_length=100, verbose_name="Qaysi shahardan")
    city_looking = models.CharField(
        max_length=100, verbose_name="Qaysi shaharda ish qidiryapti"
    )

    salary_amount = models.DecimalField(max_digits=12, decimal_places=2)
    salary_currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.UZS
    )

    contact_time_start = models.TimeField()
    contact_time_end = models.TimeField()

    purpose = models.TextField(verbose_name="Maqsad")

    status = models.CharField(
        max_length=10,
        choices=AnnouncementStatus.choices,
        default=AnnouncementStatus.PENDING,
    )
    channel_message_id = models.BigIntegerField(null=True, blank=True)
    reject_reason = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "E'lon"
        verbose_name_plural = "E'lonlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} {self.category.emoji} {self.full_name} ({self.get_status_display()})"

    def salary_display(self) -> str:
        amount = f"{self.salary_amount:,.0f}".replace(",", " ")
        if self.salary_currency == Currency.USD:
            return f"${amount}"
        return f"{amount} so'm"

    def contact_time_display(self) -> str:
        return f"{self.contact_time_start.strftime('%H:%M')}–{self.contact_time_end.strftime('%H:%M')}"
