from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from telegram_bot.models import TelegramProfile


class TelegramConnectAPIView(APIView):
    """Эндпоинт для привязки Telegram-аккаунта пользователя к его Telegram-профилю в приложении,
    когда он выбирает команду "/start" в Telegram-боте."""

    def post(self, request):
        """ ??? """
        chat_id = request.data.get("telegram_chat_id")
        user_id = request.data.get("telegram_user_id")

        if not chat_id:
            return Response({"error": "telegram_chat_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        profile, created = TelegramProfile.objects.update_or_create(
            app_user=request.user,
            defaults={
                "telegram_chat_id": chat_id,
                "telegram_user_id": user_id,
            }
        )

        return Response(
            {
                "status": "connected",
                "chat_id": profile.telegram_chat_id,
                "user": request.user.id,
                "created": created,
            },
            status=status.HTTP_200_OK,
        )
