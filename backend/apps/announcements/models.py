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
    WAITING_PAYMENT = "waiting_payment", "To'lov kutilmoqda"
    PAYMENT_PENDING = "payment_pending", "To'lov tekshirilmoqda"
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
        max_length=20,
        choices=AnnouncementStatus.choices,
        default=AnnouncementStatus.PENDING,
    )
    channel_message_id = models.BigIntegerField(null=True, blank=True)
    reject_reason = models.CharField(max_length=255, blank=True, default="")

    # Pulli (Premium) e'lon maydonlari
    is_premium = models.BooleanField(default=False, verbose_name="Pullik e'lon")
    linkedin_url = models.CharField(max_length=500, blank=True, default="", verbose_name="LinkedIn profil")
    portfolio_url = models.CharField(max_length=500, blank=True, default="", verbose_name="Portfolio")
    resume_file = models.FileField(
        upload_to="resumes/%Y/%m/", blank=True, null=True, verbose_name="Rezyume fayli"
    )
    payment_receipt = models.FileField(
        upload_to="receipts/%Y/%m/", blank=True, null=True, verbose_name="To'lov cheki"
    )
    post_count = models.PositiveSmallIntegerField(default=0, verbose_name="Chiqarilgan soni")
    next_publish_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Keyingi chiqarilish vaqti"
    )
    resume_deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Rezyume o'chirilgan vaqti"
    )

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


class PaymentSetting(models.Model):
    """Admin orqali o'zgartiriladigan to'lov (plastik karta) sozlamalari."""

    card_number = models.CharField(max_length=30, default="9860 0000 0000 0000", verbose_name="Karta raqami")
    card_owner = models.CharField(max_length=150, default="Talant24 Admin", verbose_name="Karta egasi")
    amount = models.PositiveIntegerField(default=10000, verbose_name="Narx (so'm)")
    instruction_uz = models.TextField(
        default="To'lovni ushbu plastik kartaga o'tkazib, chek skrinshotini yuboring:",
        verbose_name="Ko'rsatma (UZ)",
    )
    instruction_en = models.TextField(
        default="Transfer the payment to this card and send the receipt screenshot:",
        verbose_name="Ko'rsatma (EN)",
    )
    instruction_ru = models.TextField(
        default="Переведите оплату на эту карту и отправьте скриншот чека:",
        verbose_name="Ko'rsatma (RU)",
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "To'lov sozlamasi"
        verbose_name_plural = "To'lov sozlamalari"

    def __str__(self):
        return f"{self.card_number} ({self.card_owner}) - {self.amount} so'm"

    @classmethod
    def get_active(cls):
        setting = cls.objects.filter(is_active=True).first()
        if not setting:
            setting = cls.objects.create()
        return setting

