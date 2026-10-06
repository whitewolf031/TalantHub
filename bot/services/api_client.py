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


async def get_payment_settings() -> dict:
    async with await _client() as client:
        response = await client.get("/announcements/payment-settings/")
        response.raise_for_status()
        return response.json()


async def create_announcement(
    payload: dict,
    resume_bytes: bytes | None = None,
    resume_filename: str | None = None,
    receipt_bytes: bytes | None = None,
    receipt_filename: str | None = None,
) -> tuple[bool, dict]:
    """
    (success, data) qaytaradi. success=False bo'lsa data ichida
    xatolik tafsilotlari bo'ladi.
    """
    async with await _client() as client:
        if resume_bytes or receipt_bytes:
            files = {}
            if resume_bytes:
                files["resume_file"] = (resume_filename or "resume.pdf", resume_bytes)
            if receipt_bytes:
                files["payment_receipt"] = (receipt_filename or "receipt.jpg", receipt_bytes)

            form_data = {k: str(v) if v is not None else "" for k, v in payload.items()}
            response = await client.post("/announcements/", data=form_data, files=files)
        else:
            response = await client.post("/announcements/", json=payload)

        try:
            body = response.json()
        except Exception:
            body = {"detail": response.text}

        if response.status_code == 201:
            return True, body
        return False, {"status_code": response.status_code, "body": body}


async def get_my_announcements(telegram_id: int) -> list[dict]:
    async with await _client() as client:
        response = await client.get(f"/announcements/my/{telegram_id}/")
        response.raise_for_status()
        return response.json()


async def moderate_announcement(announcement_id: int, action: str) -> tuple[int, dict]:
    """action: 'approve' | 'reject' | 'approve-payment' | 'reject-payment'. (http_status, body) qaytaradi."""
    async with await _client() as client:
        response = await client.post(f"/announcements/{announcement_id}/{action}/", json={})
        try:
            body = response.json()
        except ValueError:
            body = {}
        return response.status_code, body


async def submit_receipt(
    announcement_id: int,
    receipt_bytes: bytes,
    receipt_filename: str = "receipt.jpg",
) -> tuple[bool, dict]:
    """To'lov chekini backendga yuklaydi."""
    async with await _client() as client:
        files = {"payment_receipt": (receipt_filename, receipt_bytes)}
        response = await client.post(f"/announcements/{announcement_id}/submit-receipt/", files=files)
        try:
            body = response.json()
        except Exception:
            body = {"detail": response.text}
        if response.status_code == 200:
            return True, body
        return False, {"status_code": response.status_code, "body": body}


async def get_waiting_payment_announcement(telegram_id: int) -> dict | None:
    """Foydalanuvchining to'lov kutilayotgan e'lonini topadi."""
    async with await _client() as client:
        try:
            response = await client.get(f"/announcements/my/{telegram_id}/")
            if response.status_code == 200:
                announcements = response.json()
                for a in announcements:
                    if a.get("status") in ("waiting_payment", "payment_pending"):
                        return a
        except Exception:
            pass
    return None


async def run_scheduler() -> dict:
    async with await _client() as client:
        try:
            response = await client.post("/announcements/run-scheduler/")
            return response.json() if response.status_code == 200 else {}
        except Exception:
            return {}

