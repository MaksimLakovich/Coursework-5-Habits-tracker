from django.urls import path

from users.views import UserViewSetAPIView

app_name = "users"

urlpatterns = [
    path("register/", UserViewSetAPIView.as_view({"post": "create"}), name="user-register"),
    path("users/<int:pk>/", UserViewSetAPIView.as_view({"get": "retrieve"}), name="user-detail"),
    path("users/<int:pk>/update/", UserViewSetAPIView.as_view({"patch": "partial_update"}), name="user-update"),
]
