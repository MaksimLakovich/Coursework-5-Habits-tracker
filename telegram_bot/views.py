from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from telegram_bot.models import TelegramProfile


class TelegramConnectAPIView(APIView):
    """API-эндпоинт для привязки Telegram-аккаунта к пользователю приложения "Трекер привычек":
    1) когда пользователь в Telegram-боте вводит команду "/start", бот берёт "chat_id" и "user_id" из Telegram API
    и отправляет их POST-запросом на этот эндпоинт "/api/telegram/connect/" добавляя в заголовок авторизационный
    токен пользователя из приложения.
    2) здесь для авторизованного пользователя создаётся или обновляется модель "TelegramProfile", чтобы мы знали,
    в какой чат отправлять напоминания о привычках."""

    def post(self, request):
        """Обрабатывает POST-запрос от Telegram-бота.

        Ожидает в теле запроса:
        - "telegram_chat_id": ID чата Telegram, куда будут приходить напоминания;
        - "telegram_user_id": уникальный ID пользователя в Telegram.

        Действия метода:
        1. Проверяет наличие "telegram_chat_id" в запросе.
        2. Использует "update_or_create", чтобы либо создать новый "TelegramProfile" для текущего пользователя
        приложения, либо обновить существующий.
        3. Возвращает JSON-ответ с результатом:
        - "created=True" - профиль был создан;
        - "created=False" - профиль уже существовал и был обновлён."""
        chat_id = request.data.get("telegram_chat_id")
        user_id = request.data.get("telegram_user_id")

        if not chat_id:
            return Response({"error": "telegram_chat_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # "update_or_create" это джанговый "шорткат", который делает 2 действия:
        #   - Ищет в базе запись с указанным пользователем (app_user=request.user).
        #   - Если запись есть → обновляет её полями из defaults={...}. Если записи нет то создаёт новую.
        # "update_or_create" возвращает два значения:
        # 1) profile - сама запись из базы;
        # 2) created - булевый флаг (True, если запись только что создана / False, если просто обновлена),
        # Под капотом метод работает так:
        #   obj, created = Model.objects.update_or_create(
        #       lookup_field=value,   # --- по чему ищем объект
        #       defaults={...}        # --- что обновляем или создаём
        #   )
        profile, created = TelegramProfile.objects.update_or_create(
            app_user=request.user,
            defaults={
                "telegram_chat_id": chat_id,
                "telegram_user_id": user_id,
            }
        )

        # В конце возвращаю JSON-ответ клиенту (боту)
        return Response(
            {
                "status": "connected",
                "chat_id": profile.telegram_chat_id,
                "user": request.user.id,
                "created": created,
            },
            status=status.HTTP_200_OK,
        )
