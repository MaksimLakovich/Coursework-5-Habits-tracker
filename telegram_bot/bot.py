"""
telegram_bot.bot
----------------
Простой Telegram-бот (aiogram v3) для привязки Telegram-чата к аккаунту в Django-приложении.

Функционал:
- /login  - интерактивно просит email и пароль, получает access/refresh у Django и сохраняет refresh локально;
- /start  - если есть сохранённый refresh, бот запрашивает новый access, вызывает Django
             эндпоинт /api/telegram/connect/ и тем самым привязывает telegram_chat_id к пользователю.

ВНИМАНИЕ:
- Используется локальное хранилище в telegram_bot/data/creds.json (подходит только для разработки).
- Переменные окружения грузятся из .env (через python-dotenv).
"""

import json
import os
from pathlib import Path
from typing import Optional, Tuple

import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (BotCommand, KeyboardButton, Message,
                           ReplyKeyboardMarkup)
from dotenv import load_dotenv

# Получаю токен телеграм-бота из .env
load_dotenv()
TELEGRAM_BOT_API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_API_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не установлен в виртуальном окружении.")

# Получаю эндпоинты из .env, если они там были указаны (например, если приложение в проде,
# то там удобно указывать это, чтоб не менять ничего в самом коде бота), а если не указаны, то использую localhost
LOGIN_URL = os.getenv("DJANGO_LOGIN_URL", "http://localhost:8000/api/login/")
REFRESH_URL = os.getenv("DJANGO_REFRESH_URL", "http://localhost:8000/api/token/refresh/")
CONNECT_URL = os.getenv("DJANGO_CONNECT_URL", "http://localhost:8000/api/telegram/connect/")

# Устанавливаю простое локальное хранилище для refresh-токенов.
# ВАЖНО: Такое решение подходит только для разработки, а для прода я бы создавал отдельную модель для хранения токенов
# пользователя в БД в зашифрованном виде (AES)
STORAGE_DIR = Path(__file__).parent / "data"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_USER_CREDENTIAL_FILE = STORAGE_DIR / "user_credential.json"


# ---------- Инициализация aiogram ----------
bot = Bot(token=TELEGRAM_BOT_API_TOKEN)
dp = Dispatcher()


# ---------- Утилиты для простого локального хранилища STORAGE_USER_CREDENTIAL_FILE ----------
def load_storage() -> dict:
    """Загружает JSON-словарь из STORAGE_USER_CREDENTIAL_FILE.
    Возвращает пустой dict, если файла нет или он пуст."""
    if STORAGE_USER_CREDENTIAL_FILE.exists():
        try:
            return json.loads(STORAGE_USER_CREDENTIAL_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_storage(data: dict) -> None:
    """Сохраняет словарь data в STORAGE_USER_CREDENTIAL_FILE в красивом формате (utf-8)."""
    STORAGE_USER_CREDENTIAL_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def set_refresh_for_user(tg_user_id: int, refresh: str) -> None:
    """Сохраняет refresh-токен для пользователя с TG ID = tg_user_id."""
    credential_storage = load_storage()
    credential_storage[str(tg_user_id)] = {"refresh": refresh}
    save_storage(credential_storage)


def get_refresh_for_user(tg_user_id: int) -> Optional[str]:
    """Возвращает сохранённый refresh для telegram user id либо None, если записи нет."""
    credential_storage = load_storage()
    user_data_in_credential_storage = credential_storage.get(str(tg_user_id))
    return user_data_in_credential_storage.get("refresh") if user_data_in_credential_storage else None


# ---------- Вспомогательные HTTP-запросы к Django API ----------
def get_tokens_by_credentials(email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
    """Логинит в Django по email/password и возвращает (access, refresh) или (None, None) при ошибке."""
    try:
        response = requests.post(LOGIN_URL, json={"email": email, "password": password}, timeout=10)
    except requests.RequestException:
        return None, None

    if response.status_code == 200:
        data = response.json()
        return data.get("access"), data.get("refresh")
    return None, None


def get_access_by_refresh(refresh: str) -> Optional[str]:
    """Обменивает refresh на новый access через /api/token/refresh/. Возвращает access или None."""
    try:
        response = requests.post(REFRESH_URL, json={"refresh": refresh}, timeout=10)
    except requests.RequestException:
        return None

    if response.status_code == 200:
        return response.json().get("access")
    return None


def connect_telegram(access: str, chat_id: int, user_id: int) -> bool:
    """Вызывает Django-эндпоинт /api/telegram/connect/ с заголовком Authorization: Bearer <access>
    и телом {"telegram_chat_id": chat_id, "telegram_user_id": user_id}.
    Возвращает True, если сервер ответил 200."""
    headers = {"Authorization": f"Bearer {access}"}
    data = {"telegram_chat_id": chat_id, "telegram_user_id": user_id}
    try:
        response = requests.post(CONNECT_URL, headers=headers, json=data, timeout=10)
    except requests.RequestException:
        return False
    return response.status_code == 200


# ---------- Главное меню ----------
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/login")],
        [KeyboardButton(text="/start")],
        [KeyboardButton(text="/help")],
    ],
    resize_keyboard=True
)


# ---------- /help:  ----------
@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Справка с доступными командами."""
    await message.answer(
        "🤖 Доступные команды:\n\n"
        "/login — авторизация в приложении\n"
        "/start — привязка аккаунта к Телеграму\n"
        "/help — показать это сообщение",
        reply_markup=main_menu
    )


# ---------- /login: процесс авторизации пользователя и FSM (конечный автомат состояний) для процесса /login ----------
class AuthFlow(StatesGroup):
    """Состояния FSM ("Finite State Machine - конечный автомат состояний") для
    последовательного ввода пользователем email и пароля в Telegram-боте."""
    waiting_email = State()
    waiting_password = State()


@dp.message(Command("login"))
async def cmd_login(message: Message, state: FSMContext) -> None:
    """/login - инициирует диалог:
    бот просит email, переходит в состояние waiting_email."""
    await message.answer("Введите email, под которым вы заходите в приложение 'Трекер привычек':")
    await state.set_state(AuthFlow.waiting_email)


@dp.message(AuthFlow.waiting_email)
async def got_email(message: Message, state: FSMContext) -> None:
    """Получает email от пользователя, сохраняет во временное состояние и просит пароль."""
    await state.update_data(email=message.text.strip())
    await message.answer("Теперь введите пароль:")
    await state.set_state(AuthFlow.waiting_password)


@dp.message(AuthFlow.waiting_password)
async def got_password(message: Message, state: FSMContext) -> None:
    """Получает пароль, делает запрос к Django /api/login/ и при успехе сохраняет refresh локально."""
    data = await state.get_data()
    email = data.get("email")
    password = message.text.strip()

    access, refresh = get_tokens_by_credentials(email, password)
    if not refresh:
        await message.answer("❌ Неверные данные или сервер недоступен. Попробуйте ещё раз: /login")
        await state.clear()
        return

    # Сохраняю refresh за этим телеграм-пользователем
    set_refresh_for_user(message.from_user.id, refresh)
    await message.answer("✅ Авторизация успешна! Теперь отправьте /start для привязки аккаунта.")
    await state.clear()


# ---------- /start: привязка TG к аккаунту ----------
@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """/start - бот получает сохранённый refresh по telegram user id, обновляет access,
    вызывает Django API /api/telegram/connect/ чтобы привязать telegram_chat_id к пользователю."""
    tg_user_id = message.from_user.id
    refresh = get_refresh_for_user(tg_user_id)

    if not refresh:
        await message.answer("Привет! Сначала авторизуйтесь: /login")
        return

    access = get_access_by_refresh(refresh)
    if not access:
        await message.answer("Не удалось обновить токен. Введите /login заново.")
        return

    ok = connect_telegram(access=access, chat_id=message.chat.id, user_id=tg_user_id)
    if ok:
        await message.answer("✅ Телеграм успешно привязан к вашему аккаунту!")
    else:
        await message.answer("❌ Ошибка при привязке. Попробуйте позже или /login")


# ---------- Установка команд для меню Telegram ----------
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="login", description="Авторизация в приложении"),
        BotCommand(command="start", description="Привязка Telegram к аккаунту"),
        BotCommand(command="help", description="Справка и список команд"),
    ]
    await bot.set_my_commands(commands)


# ---------- Запуск бота ----------
if __name__ == "__main__":
    import asyncio

    async def main():
        await set_commands(bot)
        await dp.start_polling(bot)   # это правильный метод в aiogram v3

    try:
        asyncio.run(main())
    except RuntimeError:
        # если event loop уже есть (например, PyCharm/Jupyter) - используем "прямой запуск"
        import nest_asyncio
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
