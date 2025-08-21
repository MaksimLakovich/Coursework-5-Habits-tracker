from typing import cast

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLResolver, include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # 1) namespace="users"
    # - это заданное пространство имен, которое есть в users/urls.py с помощью UsersConfig.name
    # 2) route:"api/"
    # - после "api/" ничего не указываю, так как DefaultRouter() из habits/urls.py создаст URL-ы
    # (например, /api/habits/useful_habit/)
    path("api/", include("users.urls", namespace="users")),
    path("api/", include("habits.urls", namespace="habits")),
]

if settings.DEBUG:
    urlpatterns += cast(
        list[URLResolver], static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
