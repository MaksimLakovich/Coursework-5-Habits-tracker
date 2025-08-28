from rest_framework import generics

from habits.models import Habits
from habits.paginators import (PublicHabitsListPagination,
                               UserHabitsListPagination)
from habits.permissions import IsOwner
from habits.serializers import HabitsSerializer
from telegram_bot.tasks import task_send_reminding_message


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
        # # ВАРИАНТ 1: delay() - это постой вариант для вызова отложенной celery-задачи
        # task_send_reminding_message.delay(habit.pk)
        # ВАРИАНТ 2: apply_async() - это вариант запуска отложенной celery-задачи с задержкой (например, если нужно
        # отправлять напоминания не сразу после создания, а через 2 минуты)
        task_send_reminding_message.apply_async(
            args=[habit.pk],
            countdown=60 * 2 * 1  # 2 мин
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
        # # ВАРИАНТ 1: delay() - это постой вариант для вызова отложенной celery-задачи
        # task_send_reminding_message.delay(habit.pk)
        # ВАРИАНТ 2: apply_async() - это вариант запуска отложенной celery-задачи с задержкой (например, если нужно
        # отправлять напоминания не сразу после обновления, а через 2 минуты)
        task_send_reminding_message.apply_async(
            args=[habit.pk],
            countdown=60 * 2 * 1  # 2 мин
        )
