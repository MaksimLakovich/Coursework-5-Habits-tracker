from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from users.models import AppUser
from users.serializers import AppUserSerializer


class UserViewSetAPIView(viewsets.ViewSet):
    """ViewSet-класс для создания, просмотра и редактирования пользователя в приложении."""

    def create(self, request):
        """Создание/регистрация нового пользователя в приложении."""
        serializer = AppUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        """Получение данных одного пользователя по ID."""
        user = get_object_or_404(AppUser, pk=pk)
        serializer = AppUserSerializer(user)
        return Response(serializer.data, status=200)

    def partial_update(self, request, pk=None):
        """Частичное обновление пользователя по ID."""
        user = get_object_or_404(AppUser, pk=pk)
        # Когда используется partial_update, то нужно указать partial=True, иначе будут валидироваться все поля
        serializer = AppUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
