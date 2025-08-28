from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import generics

from habits.models import Habits
from habits.paginators import (PublicHabitsListPagination,
                               UserHabitsListPagination)
from habits.permissions import IsOwner
from habits.serializers import HabitsSerializer
from telegram_bot.tasks import (REMINDER_OFFSET_MINUTES,
                                task_send_reminding_message)


class HabitsCreateAPIView(generics.CreateAPIView):
    """Класс-контроллер на основе базового Generic-класса для создания новой привычки."""

    serializer_class = HabitsSerializer

    def perform_create(self, serializer):
        """1) Присваивает текущего авторизованного пользователя как владельца (owner) создаваемого объекта.
        2) Запускает отложенную задачу по отправке напоминания о необходимости выполнения полезной привычки."""
        # 1) Установка владельца
        serializer.save(owner=self.request.user)

        # 2) Отложенная celery-задача
        habit = serializer.save()

        # # ВАРИАНТ 1: delay() - это постой вариант для вызова отложенной celery-задачи сразу в текущий момент времени
        # task_send_reminding_message.delay(habit.pk)

        # # ВАРИАНТ 2: apply_async() - это вариант запуска отложенной celery-задачи с задержкой (например, если нужно
        # # отправлять напоминания не сразу после создания, а через какое-то время).
        # task_send_reminding_message.apply_async(
        #     args=[habit.pk],
        #     countdown=60 * 2 * 1  # это будет 2 мин
        # )

        # НАПРИМЕР, я хочу чтоб напоминание отправлялось за 30 мин до времени исполнения, указанном в Привычке (можно
        # изменить 30 мин на любое другое значение в REMINDER_OFFSET_MINUTES).
        #   !!! 1) БОЛЕЕ ПРАВИЛЬНО для этого было бы использовать ПЕРИОДИЧЕСКУЮ задачу в Celery, но так как по условию
        #   БТ к курсовой сказано именно "...необходимо реализовать работу с отложенными задачами...", то сделаю
        #   в отложенной через countdown;
        #   !!! 2) Работу с периодическими задачами попрактикую в реализации рассылки всех привычек
        #   запланированных на текущий день с отправкой общего напоминания 1 раз в день (например, каждое утро).

        # Получаю текущую дату в формате "2025-08-28 13:13:37.773562+03:00"
        now = timezone.localtime()
        # Через make_aware() "наивный" datetime превращаю в "осознанный", нужно в Django для исключения ошибок в БД.
        # Получаю данные в таком формате "2025-08-28 13:18:00+03:00"
        habit_datetime = timezone.make_aware(datetime.combine(now.date(), habit.time))

        # --- если дельта между временем привычки (например, 14-15) и временем сервера (например, 13-55) это
        # положительно число, то значит эта привычка сегодня еще не прошла, а значит нужно с СЕГОДНЯ напоминать:
        if (habit_datetime - now).total_seconds() >= 0:
            countdown = (habit_datetime - now - timedelta(minutes=REMINDER_OFFSET_MINUTES)).total_seconds()
        # --- а если дельта между временем привычки (например, 12-30) и временем сервера (например, 21-55) это
        # отрицательное число, то значит на сегодня эта привычка уже в прошлом и добавляю + 1 ДЕНЬ, чтоб начать
        # напоминать с завтрашнего дня:
        else:
            countdown = ((habit_datetime - now - timedelta(minutes=REMINDER_OFFSET_MINUTES) + timedelta(days=1))
                         .total_seconds())

        # Если привычка ближе, чем offset, то отправляю сразу, т.е. countdown = 0
        # Эта часть кода сработает, когда до привычки осталось меньше времени чем указано в REMINDER_OFFSET_MINUTES
        if countdown < 0:
            countdown = 0

        task_send_reminding_message.apply_async(
            args=[habit.pk],
            countdown=countdown
        )


class UserHabitsListAPIView(generics.ListAPIView):
    """Класс-контроллер на основе базового Generic-класса для получения списка привычек текущего пользователя."""

    serializer_class = HabitsSerializer
    pagination_class = UserHabitsListPagination

    def get_queryset(self):
        """Получение набора данных, который будет использоваться во View."""
        return Habits.objects.filter(owner=self.request.user).order_by("time")


class PublicHabitsListAPIView(generics.ListAPIView):
    """Класс-контроллер на основе базового Generic-класса для получения списка публичных привычек."""

    serializer_class = HabitsSerializer
    pagination_class = PublicHabitsListPagination

    def get_queryset(self):
        """Получение набора данных, который будет использоваться во View."""
        return Habits.objects.filter(is_public=True).order_by("description")


class HabitsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Класс-контроллер на основе базового Generic-класса для просмотра, обновления и удаления конкретной привычки.
    Каждый пользователь имеет доступ только к своим привычкам по механизму CRUD."""

    queryset = Habits.objects.all()
    serializer_class = HabitsSerializer
    permission_classes = [IsOwner]

    def perform_update(self, serializer):
        """Запускает отложенную задачу по отправке напоминания о необходимости выполнения полезной привычки."""
        habit = serializer.save()

        now = timezone.localtime()
        habit_datetime = timezone.make_aware(datetime.combine(now.date(), habit.time))

        if (habit_datetime - now).total_seconds() >= 0:
            countdown = (habit_datetime - now - timedelta(minutes=REMINDER_OFFSET_MINUTES)).total_seconds()

        else:
            countdown = ((habit_datetime - now - timedelta(minutes=REMINDER_OFFSET_MINUTES) + timedelta(days=1))
                         .total_seconds())

        if countdown < 0:
            countdown = 0

        task_send_reminding_message.apply_async(
            args=[habit.pk],
            countdown=countdown
        )
