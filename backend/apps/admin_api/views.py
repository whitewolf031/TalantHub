from django.contrib.auth import authenticate
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.announcements.models import Announcement, AnnouncementStatus, PaymentSetting
from apps.announcements.services import (
    approve_announcement,
    approve_payment,
    delete_resume,
    reject_announcement,
    reject_payment,
)
from apps.categories.models import AnnouncementCategory
from apps.users.models import BotUser

from .serializers import (
    AdminAnnouncementSerializer,
    AdminAnnouncementWriteSerializer,
    AdminBotUserSerializer,
    AdminCategorySerializer,
    AdminPaymentSettingSerializer,
)


class StaffOnlyMixin:
    """Faqat is_staff=True bo'lgan foydalanuvchilar, Token orqali."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


def _user_payload(user):
    return {"username": user.username, "is_superuser": user.is_superuser}


# --- Auth -------------------------------------------------------------------

class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = request.data.get("password") or ""
        user = authenticate(request, username=username, password=password)

        if user is None or not user.is_staff:
            return Response(
                {"detail": "Username yoki parol noto'g'ri."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": _user_payload(user)})


class MeView(StaffOnlyMixin, APIView):
    def get(self, request):
        return Response(_user_payload(request.user))


class LogoutView(StaffOnlyMixin, APIView):
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Statistika (sidebar'dagi "kutilmoqda" belgisi shundan olinadi) -------------

class StatsView(StaffOnlyMixin, APIView):
    def get(self, request):
        counts = dict(
            Announcement.objects.order_by()
            .values_list("status")
            .annotate(c=Count("id"))
            .values_list("status", "c")
        )
        today = timezone.localdate()
        return Response(
            {
                "pending": counts.get(AnnouncementStatus.PENDING, 0),
                "waiting_payment": counts.get(AnnouncementStatus.WAITING_PAYMENT, 0),
                "payment_pending": counts.get(AnnouncementStatus.PAYMENT_PENDING, 0),
                "approved": counts.get(AnnouncementStatus.APPROVED, 0),
                "rejected": counts.get(AnnouncementStatus.REJECTED, 0),
                "users": BotUser.objects.count(),
                "categories": AnnouncementCategory.objects.count(),
                "new_today": Announcement.objects.filter(created_at__date=today).count(),
            }
        )


# --- E'lonlar -------------------------------------------------------------------

class AnnouncementViewSet(
    StaffOnlyMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AdminAnnouncementSerializer

    def get_queryset(self):
        qs = Announcement.objects.select_related("category", "user")
        params = self.request.query_params

        if params.get("status"):
            qs = qs.filter(status=params["status"])
        if params.get("category"):
            qs = qs.filter(category_id=params["category"])
        if params.get("search"):
            q = params["search"].strip()
            qs = qs.filter(
                Q(full_name__icontains=q)
                | Q(phone_number__icontains=q)
                | Q(telegram_username__icontains=q)
                | Q(direction__icontains=q)
                | Q(technologies__icontains=q)
            )
        # Kutilayotganlarda eng eskisi tepada (navbat tartibi), qolganlarda eng yangisi
        if params.get("status") == AnnouncementStatus.PENDING:
            return qs.order_by("created_at")
        return qs.order_by("-created_at")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AdminAnnouncementWriteSerializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.refresh_from_db()
        return Response(AdminAnnouncementSerializer(instance).data)

    def _moderation_response(self, announcement, code):
        if code in ("not_pending", "invalid_status"):
            return Response(
                {"detail": "Bu e'lon holati mos kelmaydi yoki allaqachon ko'rib chiqilgan.", "status": announcement.status},
                status=status.HTTP_409_CONFLICT,
            )
        if code == "channel_failed":
            return Response(
                {
                    "detail": "Kanalga yuborib bo'lmadi. BOT_TOKEN, CHANNEL_ID va "
                    "bot kanalda admin ekanligini tekshiring."
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )
        announcement = Announcement.objects.select_related("category", "user").get(pk=announcement.pk)
        return Response(AdminAnnouncementSerializer(announcement).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        self.get_object()
        announcement, code = approve_announcement(int(pk))
        return self._moderation_response(announcement, code)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        self.get_object()
        announcement, code = reject_announcement(int(pk), request.data.get("reason", ""))
        return self._moderation_response(announcement, code)

    @action(detail=True, methods=["post"], url_path="approve-payment")
    def approve_payment_action(self, request, pk=None):
        self.get_object()
        announcement, code = approve_payment(int(pk))
        return self._moderation_response(announcement, code)

    @action(detail=True, methods=["post"], url_path="reject-payment")
    def reject_payment_action(self, request, pk=None):
        self.get_object()
        announcement, code = reject_payment(int(pk), request.data.get("reason", ""))
        return self._moderation_response(announcement, code)

    @action(detail=True, methods=["post"], url_path="delete-resume")
    def delete_resume_action(self, request, pk=None):
        self.get_object()
        success = delete_resume(int(pk))
        if success:
            announcement = Announcement.objects.select_related("category", "user").get(pk=int(pk))
            return Response(AdminAnnouncementSerializer(announcement).data)
        return Response({"detail": "Rezyume topilmadi yoki allaqachon o'chirilgan."}, status=status.HTTP_400_BAD_REQUEST)


# --- To'lov sozlamalari (plastik karta, narx) -----------------------------------

class AdminPaymentSettingView(StaffOnlyMixin, APIView):
    def get(self, request):
        setting = PaymentSetting.get_active()
        return Response(AdminPaymentSettingSerializer(setting).data)

    def patch(self, request):
        setting = PaymentSetting.get_active()
        serializer = AdminPaymentSettingSerializer(setting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# --- E'lon turlari --------------------------------------------------------------

class CategoryViewSet(StaffOnlyMixin, viewsets.ModelViewSet):
    serializer_class = AdminCategorySerializer
    pagination_class = None

    def get_queryset(self):
        return AnnouncementCategory.objects.annotate(
            announcements_count=Count("announcements")
        ).order_by("order", "id")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
        except ProtectedError:
            return Response(
                {"detail": "Bu turda e'lonlar bor, o'chirib bo'lmaydi. Uni faolsizlantiring."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Foydalanuvchilar -----------------------------------------------------------

class BotUserViewSet(
    StaffOnlyMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AdminBotUserSerializer

    def get_queryset(self):
        qs = BotUser.objects.annotate(announcements_count=Count("announcements"))
        params = self.request.query_params

        if params.get("blocked") in ("true", "false"):
            qs = qs.filter(is_blocked=params["blocked"] == "true")
        if params.get("search"):
            q = params["search"].strip()
            filters = Q(username__icontains=q) | Q(first_name__icontains=q) | Q(phone_number__icontains=q)
            if q.isdigit():
                filters |= Q(telegram_id=int(q))
            qs = qs.filter(filters)
        return qs.order_by("-created_at")

    @action(detail=True, methods=["post"], url_path="toggle-block")
    def toggle_block(self, request, pk=None):
        user = self.get_object()
        user.is_blocked = not user.is_blocked
        user.save(update_fields=["is_blocked", "updated_at"])
        user = self.get_queryset().get(pk=user.pk)
        return Response(AdminBotUserSerializer(user).data)
