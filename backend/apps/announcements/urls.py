from django.urls import path

from .views import (
    AnnouncementCreateView,
    AnnouncementModerateView,
    LastAnnouncementStatusView,
    UserAnnouncementListView,
)

urlpatterns = [
    path("", AnnouncementCreateView.as_view(), name="announcement-create"),
    path(
        "cooldown/<int:telegram_id>/",
        LastAnnouncementStatusView.as_view(),
        name="announcement-cooldown",
    ),
    path(
        "my/<int:telegram_id>/",
        UserAnnouncementListView.as_view(),
        name="announcement-my-list",
    ),
    path(
        "<int:pk>/approve/",
        AnnouncementModerateView.as_view(moderation="approve"),
        name="announcement-approve",
    ),
    path(
        "<int:pk>/reject/",
        AnnouncementModerateView.as_view(moderation="reject"),
        name="announcement-reject",
    ),
]
