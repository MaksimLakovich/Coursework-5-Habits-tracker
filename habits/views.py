from rest_framework import generics

from habits.models import Habits
from habits.paginators import (PublicHabitsListPagination,
                               UserHabitsListPagination)
from habits.permissions import IsOwner
from habits.serializers import HabitsSerializer
from habits.services import set_param_countdown
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

        task_send_reminding_message.apply_async(
            args=[habit.pk],
            countdown=set_param_countdown(habit)  # Рассчитываю countdown для каждой привычки в set_param_countdown()
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
        """Запускает отложенную задачу по отправке напоминания о необходимости выполнения полезной привычки.
        *countdown* рассчитывается автоматически для каждой привычки."""
        habit = serializer.save()

        task_send_reminding_message.apply_async(
            args=[habit.pk],
            countdown=set_param_countdown(habit)  # Рассчитываю countdown для каждой привычки в set_param_countdown()
        )
