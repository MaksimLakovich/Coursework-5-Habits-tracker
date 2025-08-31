from unittest.mock import patch
from django.test import TestCase

from telegram_bot.services import send_telegram_message


class TelegramBotServicesTests(TestCase):
    """Тесты, которые будут проверять работу сервисов Telegram-бота."""

    @patch("telegram_bot.services.requests.get")
    def test_send_telegram_message(self, mock_get):
        """Тест, что сервисная функция send_telegram_message() вызывает requests.get с правильными параметрами."""
        chat_id = "123456789"
        message = "Это тестовое сообщение."

        send_telegram_message(chat_id, message)

        # Проверяю, что requests.get вызван ровно 1 раз
        mock_get.assert_called_once()

        # Достаю параметры вызова
        args, kwargs = mock_get.call_args

        # Проверяю, что в URL используется метод sendMessage
        self.assertIn("sendMessage", args[0])

        # Проверяю, что chat_id и text передаются корректно
        self.assertEqual(kwargs["params"]["chat_id"], chat_id)
        self.assertEqual(kwargs["params"]["text"], message)
