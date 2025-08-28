from datetime import datetime, timedelta

from celery import shared_task  # type: ignore
from django.utils import timezone

from habits.models import Habits
from telegram_bot.models import TelegramProfile
from telegram_bot.services import send_telegram_message

REMINDER_OFFSET_MINUTES = 30  # за сколько минут до привычки присылать напоминание


@shared_task(bind=True, max_retries=3)
def task_send_reminding_message(self, habit_id):
    """Напоминание о необходимости выполнения полезной привычки.
    :param habit_id: ID привычки, для которой нужно отправить напоминание.
    """
    habit = Habits.objects.get(id=habit_id)
    # Если место в привычке не указано пользователем, то использую это по умолчанию
    location = habit.location or "место не указано"
    message = (f"Напоминание! Запланировано: {habit.description} в {habit.time} (место: {location}).")

    if not habit.owner:
        return  # На всякий случай: привычка без владельца

    try:
        # get() принимает ключ=значение, а не сам объект. Поэтому просто get(habit.owner) не сработает
        tg_profile = TelegramProfile.objects.get(app_user=habit.owner)
        chat_id = tg_profile.telegram_chat_id
        if not chat_id:
            return

        now_time = timezone.localtime().time()  # текущее время в формате HH:MM:SS
        habit_time = habit.time  # время в модели самой привычки

        # Превращаю оба time в datetime, чтоб потом можно было вычислить разницу и чтоб это было без учета ДАТЫ, а
        # только по ВРЕМЯ, добавляю и там и там одинаковую дату = "0001-01-01"
        today = datetime.min.date()

        now_dt = datetime.combine(today, now_time)
        habit_dt = datetime.combine(today, habit_time)
        delta = habit_dt - now_dt

        if timedelta(minutes=0) <= delta <= timedelta(minutes=REMINDER_OFFSET_MINUTES):
            send_telegram_message(chat_id, message)

    except TelegramProfile.DoesNotExist:
        return

    except Exception as e:
        # Повтор через 120 секунд, максимум 3 попытки согласно "max_retries=3"
        raise self.retry(exc=e, countdown=120)
