from datetime import timedelta

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import BotUser

from .models import Announcement
from .serializers import AnnouncementCreateSerializer, AnnouncementReadSerializer
from .services import approve_announcement, reject_announcement


def _cooldown_remaining(user):
    """Foydalanuvchi qayta e'lon joylashi uchun qolgan vaqt (timedelta) yoki None."""
    last_approved = user.last_approved_announcement()
    if not last_approved or not last_approved.approved_at:
        return None
    cooldown = timedelta(hours=settings.ANNOUNCEMENT_COOLDOWN_HOURS)
    elapsed = timezone.now() - last_approved.approved_at
    return cooldown - elapsed if elapsed < cooldown else None


class AnnouncementCreateView(APIView):
    """
    POST /api/announcements/
    Yangi e'lon yaratadi (status=pending). Bloklangan foydalanuvchiga 403,
    cooldown tugamagan bo'lsa 429 qaytaradi.
    """

    def post(self, request):
        user = BotUser.objects.filter(telegram_id=request.data.get("telegram_id")).first()

        if user:
            if user.is_blocked:
                return Response({"detail": "blocked"}, status=status.HTTP_403_FORBIDDEN)

            remaining = _cooldown_remaining(user)
            if remaining:
                return Response(
                    {"detail": "cooldown", "remaining_seconds": int(remaining.total_seconds())},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

        serializer = AnnouncementCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        announcement = serializer.save()
        return Response(
            AnnouncementReadSerializer(announcement).data,
            status=status.HTTP_201_CREATED,
        )


class LastAnnouncementStatusView(APIView):
    """GET /api/announcements/cooldown/<telegram_id>/ — bot e'lon boshlashdan oldin tekshiradi."""

    def get(self, request, telegram_id):
        user = BotUser.objects.filter(telegram_id=telegram_id).first()
        if not user:
            return Response({"can_post": True, "remaining_seconds": 0, "blocked": False})

        if user.is_blocked:
            return Response({"can_post": False, "remaining_seconds": 0, "blocked": True})

        remaining = _cooldown_remaining(user)
        if not remaining:
            return Response({"can_post": True, "remaining_seconds": 0, "blocked": False})

        return Response(
            {"can_post": False, "remaining_seconds": int(remaining.total_seconds()), "blocked": False}
        )


class UserAnnouncementListView(APIView):
    """GET /api/announcements/my/<telegram_id>/ — profil bo'limi uchun."""

    def get(self, request, telegram_id):
        announcements = (
            Announcement.objects.filter(user__telegram_id=telegram_id)
            .select_related("category", "user")
            .order_by("-created_at")[:20]
        )
        return Response(AnnouncementReadSerializer(announcements, many=True).data)


class AnnouncementModerateView(APIView):
    """
    POST /api/announcements/<id>/approve/
    POST /api/announcements/<id>/reject/
    Telegramdagi admin tugmalari (bot) shu endpointlarni chaqiradi.
    """

    moderation = None  # "approve" | "reject"

    def post(self, request, pk):
        get_object_or_404(Announcement, pk=pk)

        if self.moderation == "approve":
            announcement, code = approve_announcement(pk)
        else:
            announcement, code = reject_announcement(pk, request.data.get("reason", ""))

        if code == "not_pending":
            return Response(
                {"detail": "not_pending", "status": announcement.status},
                status=status.HTTP_409_CONFLICT,
            )
        if code == "channel_failed":
            return Response(
                {"detail": "channel_failed"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(AnnouncementReadSerializer(announcement).data)
