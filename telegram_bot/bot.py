import asyncio

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# !!!!!!! - Пока токен жёстко забит (надо подумать, как его передать из env, пока не получается через os.getenv()).
API_TOKEN = "8474530010:AAEHVQBL-RlxcQ7xmCV--ugNB8ABjTiF18A"
DJANGO_API_URL = "http://localhost:8000/api/telegram/connect/"

# !!!!!!! - Пока токен жёстко забит (надо подумать, как его хранить безопасно)
USER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2NzQ3Nzc4LCJpYXQiOjE3NTY3MzY5NzgsImp0aSI6Ijg5ZWFhOWU3Y2UwMzQ3M2ZiM2ZlMjAxZmY4M2NkYzJkIiwidXNlcl9pZCI6IjEwIn0.4eN79pmU1ZK4TjIb4WpilMgd4oa44p5kd4qicc6aQ1E"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обработчик команды /start в Телеграм-боте, которая вызывает эндпоинт TelegramConnectAPIView
    (привязка Telegram-аккаунта пользователя к его Telegram-профилю в нашем приложении)."""
    chat_id = message.chat.id
    user_id = message.from_user.id

    headers = {"Authorization": f"Bearer {USER_TOKEN}"}
    data = {"telegram_chat_id": chat_id, "telegram_user_id": user_id}

    try:
        response = requests.post(DJANGO_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            await message.answer("Ваш Telegram успешно привязан к аккаунту приложения!")
        else:
            await message.answer(f"Ошибка при привязке: {response.text}")
    except Exception as e:
        await message.answer("Не удалось связаться с сервером, попробуйте позже.")


async def main():
    # Запускаю цикл обработки апдейтов
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
