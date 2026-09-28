from django.db import models


class AnnouncementCategory(models.Model):
    """
    E'lon turi (kategoriya). Bazaviy 5 ta bo'limdan tashqari, admin
    kelajakda Django admin orqali yangi kategoriya qo'shishi mumkin —
    kod o'zgartirish shart emas.
    """

    key = models.SlugField(
        max_length=50,
        unique=True,
        help_text="Ichki kalit, masalan: job_seeker, mentor_needed",
    )
    emoji = models.CharField(max_length=8, default="📢")
    name_uz = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "E'lon turi"
        verbose_name_plural = "E'lon turlari"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.emoji} {self.name_uz}"

    def name_for(self, language: str) -> str:
        return {
            "uz": self.name_uz,
            "en": self.name_en,
            "ru": self.name_ru,
        }.get(language, self.name_uz)

    def display_title(self, language: str = "uz") -> str:
        return f"{self.emoji} {self.name_for(language)}"
