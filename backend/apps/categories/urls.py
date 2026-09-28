from django.urls import path

from .views import ActiveCategoryListView

urlpatterns = [
    path("", ActiveCategoryListView.as_view(), name="category-list"),
]
