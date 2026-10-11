import uuid
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BotUser, ReferralCampaign
from .serializers import (
    BotUserRegisterSerializer,
    BotUserSerializer,
    ReferralCampaignSerializer,
)


class UserRegisterView(APIView):
    """
    POST /api/users/register/
    Foydalanuvchi /start bosganda chaqiriladi: mavjud bo'lsa yangilanadi,
    bo'lmasa yangi yaratiladi.
    """

    def post(self, request):
        serializer = BotUserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = BotUserSerializer(user).data
        if getattr(serializer, "referral_event", None):
            data["referral_event"] = serializer.referral_event
        return Response(data, status=status.HTTP_200_OK)


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH /api/users/<telegram_id>/
    Masalan tilni o'zgartirish uchun: PATCH {"language": "en"}
    """

    queryset = BotUser.objects.all()
    serializer_class = BotUserSerializer
    lookup_field = "telegram_id"

    def patch(self, request, *args, **kwargs):
        # last_activity_at avtomatik auto_now bilan yangilanadi
        return self.partial_update(request, *args, **kwargs)


class ReferralStatusView(APIView):
    """
    GET /api/users/<telegram_id>/referral/
    Foydalanuvchining joriy taklif kampaniyasi holatini qaytaradi.
    """

    def get(self, request, telegram_id):
        user = get_object_or_404(BotUser, telegram_id=telegram_id)
        now = timezone.now()

        latest_campaign = user.referral_campaigns.order_by("-created_at").first()

        # Faol kampaniyani tekshirish
        if latest_campaign and latest_campaign.is_active:
            if latest_campaign.is_expired:
                latest_campaign.is_active = False
                latest_campaign.save(update_fields=["is_active"])
            else:
                return Response({
                    "status": "active",
                    "code": latest_campaign.code,
                    "invited_count": latest_campaign.invited_count,
                    "target_count": latest_campaign.target_count,
                    "expires_at": latest_campaign.expires_at,
                    "remaining_seconds": max(0, int((latest_campaign.expires_at - now).total_seconds())),
                    "free_premium_posts": user.free_premium_posts,
                })

        # Agar faol kampaniya bo'lmasa, 1 oylik (30 kunlik) cooldown tekshiriladi
        if latest_campaign:
            cooldown_end = latest_campaign.created_at + timedelta(days=30)
            if now < cooldown_end:
                remaining_seconds = max(0, int((cooldown_end - now).total_seconds()))
                return Response({
                    "status": "cooldown",
                    "cooldown_until": cooldown_end,
                    "remaining_seconds": remaining_seconds,
                    "free_premium_posts": user.free_premium_posts,
                    "last_invited_count": latest_campaign.invited_count,
                    "last_rewarded": latest_campaign.is_rewarded,
                })

        # 30 kun o'tgan yoki kampaniya hali ochilmagan — yangi ochish mumkin
        return Response({
            "status": "can_create",
            "free_premium_posts": user.free_premium_posts,
        })


class CreateReferralCampaignView(APIView):
    """
    POST /api/users/<telegram_id>/referral/create/
    Yangi 7 kunlik taklif havolasini yaratadi (1 oyda 1 marta ruxsat beriladi).
    """

    def post(self, request, telegram_id):
        user = get_object_or_404(BotUser, telegram_id=telegram_id)
        now = timezone.now()

        latest_campaign = user.referral_campaigns.order_by("-created_at").first()
        if latest_campaign and latest_campaign.is_active and not latest_campaign.is_expired:
            return Response(
                {
                    "detail": "Faol kampaniya allaqachon mavjud",
                    "code": latest_campaign.code,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if latest_campaign:
            cooldown_end = latest_campaign.created_at + timedelta(days=30)
            if now < cooldown_end:
                remaining_seconds = max(0, int((cooldown_end - now).total_seconds()))
                return Response(
                    {
                        "detail": "1 oylik muddat tugamagan",
                        "remaining_seconds": remaining_seconds,
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

        code = f"ref_{user.telegram_id}_{uuid.uuid4().hex[:6]}"
        campaign = ReferralCampaign.objects.create(
            user=user,
            code=code,
            expires_at=now + timedelta(days=7),
            target_count=5,
        )

        return Response({
            "status": "active",
            "code": campaign.code,
            "invited_count": 0,
            "target_count": 5,
            "expires_at": campaign.expires_at,
            "remaining_seconds": int((campaign.expires_at - now).total_seconds()),
            "free_premium_posts": user.free_premium_posts,
        }, status=status.HTTP_201_CREATED)

