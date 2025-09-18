from django.db import models

from config import settings
from habits.models import TimeStampedModel


class TelegramProfile(TimeStampedModel):
    """Модель *TelegramProfile* представляет телеграм-профиль пользователя в приложении."""

    app_user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_telegram_profile",
        verbose_name="Пользователь приложения:",
        help_text="Укажите пользователя приложения",
    )
    telegram_chat_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Telegram ChatID:",
        help_text="Укажите ChatID пользователя приложения в Telegram (куда шлём сообщения)",
    )
    telegram_user_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Telegram UserID:",
        help_text="Укажите UserID пользователя приложения в Telegram (опционально)",
    )

    def __str__(self):
        """Метод определяет строковое представление объекта. Полезно для отображения объектов в админке/консоли."""
        return f"{self.app_user} (Telegram ChatID: {self.telegram_chat_id})"

    class Meta:
        verbose_name = "Телеграм-профиль"
        verbose_name_plural = "Телеграм-профили"
        ordering = ["app_user"]
