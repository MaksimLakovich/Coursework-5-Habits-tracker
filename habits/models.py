from django.db import models

from config import settings


class TimeStampedModel(models.Model):
    """Абстрактная базовая модель для дальнейшего создания *created_at* и *updated_at* во всех моделях приложения."""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания:",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления:",
    )

    class Meta:
        """Обязательный параметр для абстрактных базовых моделей."""
        abstract = True


class Habits(TimeStampedModel):
    """Модель *Habits* представляет привычку пользователя в приложении."""

    # Использую строку в to="users.AppUser" (рекомендуется для ForeignKey к User) вместо to=AppUser, чтоб
    # избежать ошибки циклического импорта (circular import), которая может возникнуть из-за того, что
    # в "users/models.py" появится, например, "from habits.models import Telegram"
    owner = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="owned_habits",
        verbose_name="Владелец:",
        help_text="Укажите пользователя, создавшего привычку",
    )
    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Место:",
        help_text="Укажите место выполнения привычки",
    )
    time = models.TimeField(
        null=False,
        blank=False,
        verbose_name="Время:",
        help_text="Укажите время выполнения привычки",
    )
    description = models.TextField(
        null=False,
        blank=False,
        verbose_name="Действие:",
        help_text="Укажите действие, которое представляет собой привычка",
    )
    is_pleasant = models.BooleanField(
        default=False,
        null=False,
        blank=False,
        verbose_name="Признак приятной привычки:",
        help_text="Привычка, которую можно привязать к выполнению полезной привычки",
    )
    related_pleasant_habit = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_habits",
        verbose_name="Связанная приятная привычка:",
        help_text="Приятная привычка, которая связана с полезной привычкой",
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        null=False,
        blank=False,
        verbose_name="Периодичность:",
        help_text="Периодичность выполнения привычки (в днях)",
    )
    reward = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Вознаграждение:",
        help_text="Чем пользователь должен себя вознаградить после выполнения",
    )
    time_to_complete = models.PositiveSmallIntegerField(
        null=False,
        verbose_name="Время на выполнение:",
        help_text="Время, которое предположительно потратит пользователь на выполнение привычки (в секундах)",
    )
    is_public = models.BooleanField(
        default=False,
        null=False,
        blank=False,
        verbose_name="Признак публичности:",
        help_text="Привычки можно публиковать в общий доступ",
    )

    def __str__(self):
        """Метод определяет строковое представление объекта. Полезно для отображения объектов в админке/консоли."""
        return f"{self.description}"

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["time", "description"]
