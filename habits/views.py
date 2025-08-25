from rest_framework import generics

from habits.models import Habits
from habits.paginators import (PublicHabitsListPagination,
                               UserHabitsListPagination)
from habits.permissions import IsOwner
from habits.serializers import HabitsSerializer


class HabitsCreateAPIView(generics.CreateAPIView):
    """Класс-контроллер на основе базового Generic-класса для создания новой привычки."""

    serializer_class = HabitsSerializer

    def perform_create(self, serializer):
        """Присваивает текущего авторизованного пользователя как владельца (owner) создаваемого объекта."""
        serializer.save(owner=self.request.user)


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
