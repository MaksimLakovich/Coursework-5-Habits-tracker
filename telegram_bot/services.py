import requests

from config.settings import TELEGRAM_API_URL, TELEGRAM_BOT_TOKEN


def send_telegram_message(chat_id, message):
    """Отправляет сообщение пользователю в Telegram.
    :param chat_id: Telegram ChatID пользователя.
    :param message: Текст сообщения в Telegram.
    """
    url = f"{TELEGRAM_API_URL}{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": message,
    }
    requests.get(url, params=params)
