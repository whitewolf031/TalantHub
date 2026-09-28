from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    AnnouncementViewSet,
    BotUserViewSet,
    CategoryViewSet,
    LoginView,
    LogoutView,
    MeView,
    StatsView,
)

router = SimpleRouter()
router.register("announcements", AnnouncementViewSet, basename="admin-announcement")
router.register("categories", CategoryViewSet, basename="admin-category")
router.register("users", BotUserViewSet, basename="admin-user")

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="admin-login"),
    path("auth/me/", MeView.as_view(), name="admin-me"),
    path("auth/logout/", LogoutView.as_view(), name="admin-logout"),
    path("stats/", StatsView.as_view(), name="admin-stats"),
    path("", include(router.urls)),
]
