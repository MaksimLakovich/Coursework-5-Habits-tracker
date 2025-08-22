from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import UserTokenObtainPairView, UserViewSetAPIView

app_name = "users"

urlpatterns = [
    path("login/", UserTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", UserViewSetAPIView.as_view({"post": "create"}), name="user-register"),
    path("users/<int:pk>/", UserViewSetAPIView.as_view({"get": "retrieve"}), name="user-detail"),
    path("users/<int:pk>/update/", UserViewSetAPIView.as_view({"patch": "partial_update"}), name="user-update"),
    path("users/<int:pk>/set_password/", UserViewSetAPIView.as_view({"post": "user_set_password"}), name="user-set-password"),
]
