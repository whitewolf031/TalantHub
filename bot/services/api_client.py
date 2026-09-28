"""
Django backend bilan muloqot qiluvchi HTTP klient.
Bot hech qachon ma'lumotlar bazasiga to'g'ridan-to'g'ri ulanmaydi —
faqat shu klient orqali backend API'siga murojaat qiladi
(microservice arxitektura talabiga ko'ra).
"""
import httpx

from config import BACKEND_API_URL, INTERNAL_API_KEY

HEADERS = {"X-Internal-Api-Key": INTERNAL_API_KEY}


async def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=BACKEND_API_URL, headers=HEADERS, timeout=10)


async def register_user(telegram_id: int, username: str | None, first_name: str | None, language: str) -> dict:
    async with await _client() as client:
        response = await client.post(
            "/users/register/",
            json={
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "language": language,
            },
        )
        response.raise_for_status()
        return response.json()


async def get_user(telegram_id: int) -> dict | None:
    async with await _client() as client:
        response = await client.get(f"/users/{telegram_id}/")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()


async def update_language(telegram_id: int, language: str) -> dict:
    async with await _client() as client:
        response = await client.patch(
            f"/users/{telegram_id}/", json={"language": language}
        )
        response.raise_for_status()
        return response.json()


async def touch_activity(telegram_id: int) -> None:
    """last_activity_at ni yangilash uchun yengil so'rov."""
    async with await _client() as client:
        await client.patch(f"/users/{telegram_id}/", json={})


async def get_categories() -> list[dict]:
    async with await _client() as client:
        response = await client.get("/categories/")
        response.raise_for_status()
        return response.json()


async def check_cooldown(telegram_id: int) -> dict:
    async with await _client() as client:
        response = await client.get(f"/announcements/cooldown/{telegram_id}/")
        response.raise_for_status()
        return response.json()


async def create_announcement(payload: dict) -> tuple[bool, dict]:
    """
    (success, data) qaytaradi. success=False bo'lsa data ichida
    xatolik tafsilotlari (masalan cooldown yoki validatsiya xatosi) bo'ladi.
    """
    async with await _client() as client:
        response = await client.post("/announcements/", json=payload)
        if response.status_code == 201:
            return True, response.json()
        return False, {"status_code": response.status_code, "body": response.json()}


async def get_my_announcements(telegram_id: int) -> list[dict]:
    async with await _client() as client:
        response = await client.get(f"/announcements/my/{telegram_id}/")
        response.raise_for_status()
        return response.json()


async def moderate_announcement(announcement_id: int, action: str) -> tuple[int, dict]:
    """action: 'approve' | 'reject'. (http_status, body) qaytaradi."""
    async with await _client() as client:
        response = await client.post(f"/announcements/{announcement_id}/{action}/", json={})
        try:
            body = response.json()
        except ValueError:
            body = {}
        return response.status_code, body
