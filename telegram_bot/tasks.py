from datetime import datetime, timedelta

from celery import shared_task  # type: ignore
from django.utils import timezone

from habits.models import Habits
from telegram_bot.models import TelegramProfile
from telegram_bot.services import send_telegram_message

REMINDER_OFFSET_MINUTES = 30  # за сколько минут до привычки присылать напоминание


@shared_task(bind=True, max_retries=3)
def task_send_reminding_message(self, habit_id):
    """Напоминание о необходимости выполнения полезной привычки. Учитывается периодичность выполнения привычки.
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

        # ШАГ 1 -  ПРОИСХОДИТ ПЕРВАЯ ОТПРАВКА НАПОМИНАНИЯ
        send_telegram_message(chat_id, message)

        # ШАГ 2 - ПРОИСХОДЯТ ПОСЛЕДУЮЩИЕ УВЕДОМЛЕНИЯ С УЧЕТО ЗНАЧЕНИЯ В ПАРАМЕТРЕ PERIODICITY.
        # periodicity в модели Habit хранит значение от 1 до 7, где: 1 - каждый день, 7 - раз в неделю.
        if habit.periodicity:
            # 2.1. Сразу определяю текущую дату и время. Например, 2025-08-28 15:48:01.410876+03:00
            now = timezone.localtime()
            # 2.2. Потом устанавливаю следующую дату исполнения привычки с учетом указанной ПЕРИОДИЧНОСТИ.
            # Например, если у привычки periodicity=2, то получится 2025-08-30
            next_date = now.date() + timedelta(days=habit.periodicity)
            # 2.3. Потом через make_aware() "наивный" datetime превращаю в "осознанный", что нужно в Django для
            # исключения ошибок в БД и создаю для привычки следующую дату и время. Например, 2025-08-30 16:00:00+03:00.
            # В таком формате нужно, чтоб потом сработал timedelta.
            habit_datetime = timezone.make_aware(datetime.combine(next_date, habit.time))
            # 2.4. Потом определяю countdown для функции отправки уведомления.
            # Например, для "через 2 дня, но за 30 мин до будет такое значение: 171718.589124
            countdown = (habit_datetime - now - timedelta(minutes=REMINDER_OFFSET_MINUTES)).total_seconds()
            # 2.5. И в завершение выполняю "перезапись" отложенной задачи но уже с новым countdown на будущее.
            # Так получаю бесконечный цикл напоминаний, пока привычка существует.
            if countdown > 0:
                task_send_reminding_message.apply_async(args=[habit.pk], countdown=countdown)

    except TelegramProfile.DoesNotExist:
        return

    except Exception as e:
        # Повтор через 120 секунд, максимум 3 попытки согласно "max_retries=3"
        raise self.retry(exc=e, countdown=120)
