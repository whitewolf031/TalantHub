from rest_framework import generics

from .models import AnnouncementCategory
from .serializers import AnnouncementCategorySerializer


class ActiveCategoryListView(generics.ListAPIView):
    """GET /api/categories/  — botdagi kategoriya tugmalari uchun."""

    serializer_class = AnnouncementCategorySerializer
    pagination_class = None

    def get_queryset(self):
        return AnnouncementCategory.objects.filter(is_active=True).order_by("order", "id")
