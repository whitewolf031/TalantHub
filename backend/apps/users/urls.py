from django.urls import path

from .views import UserDetailView, UserRegisterView

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="user-register"),
    path("<int:telegram_id>/", UserDetailView.as_view(), name="user-detail"),
]
