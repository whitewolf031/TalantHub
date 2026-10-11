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
    free_premium_posts = models.PositiveIntegerField(
        default=0, verbose_name="Bepul premium e'lonlar soni"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name or 'NoName'} (@{self.username or '—'}) [{self.telegram_id}]"

    def last_approved_announcement(self, is_premium=None):
        qs = self.announcements.filter(status="approved")
        if is_premium is not None:
            qs = qs.filter(is_premium=is_premium)
        return qs.order_by("-approved_at").first()


class ReferralCampaign(models.Model):
    user = models.ForeignKey(
        BotUser,
        on_delete=models.CASCADE,
        related_name="referral_campaigns",
        verbose_name="Foydalanuvchi",
    )
    code = models.CharField(
        max_length=64, unique=True, db_index=True, verbose_name="Taklif kodi"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    expires_at = models.DateTimeField(verbose_name="Tugash vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    is_rewarded = models.BooleanField(default=False, verbose_name="Mukofot berilgan")
    target_count = models.PositiveIntegerField(default=5, verbose_name="Maqsad soni")

    class Meta:
        verbose_name = "Taklif kampaniyasi"
        verbose_name_plural = "Taklif kampaniyalari"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ({self.code}) - {self.invited_count}/{self.target_count}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def invited_count(self):
        return self.referrals.count()


class Referral(models.Model):
    campaign = models.ForeignKey(
        ReferralCampaign,
        on_delete=models.CASCADE,
        related_name="referrals",
        verbose_name="Kampaniya",
    )
    inviter = models.ForeignKey(
        BotUser,
        on_delete=models.CASCADE,
        related_name="invited_referrals",
        verbose_name="Taklif qiluvchi",
    )
    referred_user = models.OneToOneField(
        BotUser,
        on_delete=models.CASCADE,
        related_name="referred_by",
        verbose_name="Taklif qilingan foydalanuvchi",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqt")

    class Meta:
        verbose_name = "Taklif qilingan do'st"
        verbose_name_plural = "Taklif qilingan do'stlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.referred_user} <- {self.inviter}"

