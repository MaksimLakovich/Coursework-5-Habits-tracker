from django.urls import path
from telegram_bot.views import TelegramConnectAPIView

app_name = "telegram_bot"

urlpatterns = [
    path("telegram/connect/", TelegramConnectAPIView.as_view(), name="telegram-connect"),
]
