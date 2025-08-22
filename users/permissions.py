from rest_framework.permissions import BasePermission


class IsSelf(BasePermission):
    """Разрешает доступ только владельцу своего профиля."""

    message = "У вас нет прав на действия с чужим профилем."

    def has_object_permission(self, request, view, obj):
        """Возвращает True, если пользователь совпадает с данными в запрашиваемом объекте.
        Используется в контроллерах для ограничения доступа к чужим профилям."""
        return obj == request.user
