from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BotUser
from .serializers import BotUserRegisterSerializer, BotUserSerializer


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
        return Response(
            BotUserSerializer(user).data,
            status=status.HTTP_200_OK,
        )


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
