from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("apps.users.urls")),
    path("api/categories/", include("apps.categories.urls")),
    path("api/announcements/", include("apps.announcements.urls")),
    # React admin panel uchun API (Token auth, faqat staff)
    path("api/admin/", include("apps.admin_api.urls")),
]
