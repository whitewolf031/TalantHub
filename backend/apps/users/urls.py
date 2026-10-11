from django.urls import path

from .views import (
    CreateReferralCampaignView,
    ReferralStatusView,
    UserDetailView,
    UserRegisterView,
)

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="user-register"),
    path("<int:telegram_id>/", UserDetailView.as_view(), name="user-detail"),
    path("<int:telegram_id>/referral/", ReferralStatusView.as_view(), name="user-referral-status"),
    path("<int:telegram_id>/referral/create/", CreateReferralCampaignView.as_view(), name="user-referral-create"),
]

