from django.conf import settings
from rest_framework.permissions import BasePermission

INTERNAL_API_KEY_HEADER = "X-Internal-Api-Key"


class InternalAPIKeyPermission(BasePermission):
    """
    Faqat TalantHub botidan (yoki boshqa ichki xizmatdan) kelayotgan
    so'rovlarga ruxsat beradi. Har bir so'rovda quyidagi header bo'lishi shart:

        X-Internal-Api-Key: <INTERNAL_API_KEY>

    Bu API tashqi foydalanuvchilar uchun emas, faqat bot <-> backend
    muloqoti uchun mo'ljallangan.
    """

    message = "Ichki API kaliti noto'g'ri yoki mavjud emas."

    def has_permission(self, request, view):
        provided_key = request.headers.get(INTERNAL_API_KEY_HEADER, "")
        return bool(provided_key) and provided_key == settings.INTERNAL_API_KEY
