from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Кастомный permission-класс, проверяющий, является ли пользователь владельцем (owner) объекта."""

    message = "У вас нет прав на изменение или удаление чужих привычек."

    def has_object_permission(self, request, view, obj):
        """Возвращает True, если пользователь является владельцем объекта.
        Используется в контроллерах для ограничения доступа к чужим объектам."""

        return obj.owner == request.user
