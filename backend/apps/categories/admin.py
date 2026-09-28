from django.contrib import admin

from .models import AnnouncementCategory


@admin.register(AnnouncementCategory)
class AnnouncementCategoryAdmin(admin.ModelAdmin):
    list_display = ("emoji", "name_uz", "name_en", "name_ru", "key", "is_active", "order")
    list_editable = ("is_active", "order")
    search_fields = ("key", "name_uz", "name_en", "name_ru")
