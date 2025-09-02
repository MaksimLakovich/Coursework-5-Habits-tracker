from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import AppUser
from users.permissions import IsSelf
from users.serializers import AppUserSerializer, UserObtainPairSerializer


class UserViewSetAPIView(viewsets.ViewSet):
    """ViewSet-класс для создания, просмотра и редактирования пользователя в приложении."""

    def get_permissions(self):
        """Определяет права доступа в зависимости от действия:
        - create;
        - retrieve;
        - partial_update;
        - user_set_password."""
        if self.action == "create":
            return [AllowAny()]
        elif self.action in ["retrieve", "partial_update", "user_set_password"]:
            return [IsAuthenticated(), IsSelf()]
        return super().get_permissions()

    # ПОЯСНЕНИЯ:
    # 1) IsSelf() - это объектный permission, а в DRF во ***viewsets.ViewSet*** объектные пермишены НЕ вызываются
    # автоматически! Их нужно явно проверять через ***self.check_object_permissions(request, obj)***.
    # 2) БЫЛО БЫ ПРОЩЕ ИЗНАЧАЛЬНО ИСПОЛЬЗВАТЬ ***GenericViewSet***, где это делает get_object() автоматически, НО ДЛЯ
    # СВОЕЙ ПРАКТИКИ Я ОСОЗНАНО ДЛЯ ДАННОЙ МОДЕЛИ ВЫБРАЛ - ***viewsets.ViewSet***, ТАК КАК НЕ ПРАКТИКОВАЛ ЭТО В ДРУГИХ
    # ЗАДАНИЯХ РАНЕЕ.
    # 3) Если в ***retrieve/partial_update*** сделать через ***get_object_or_404(...)*** без переопределения
    # метода ***def get_object(self)*** с вызовом ***self.check_object_permissions(...)***, то IsSelf() просто
    # не сработает там и будет ДОСТУП у любого пользователя к любому профилю.
    # 4) Можно не описывать ***def get_object(self)***, а добавить оставить ***check_object_permissions***
    # в ***retrieve*** и ***0partial_update***, вот так:
    #     user = get_object_or_404(AppUser, pk=pk)
    #     self.check_object_permissions(self.request, user)
    # но тогда я дублирую строки кода, что не соответствует правилу: "донт репит себя".
    def get_object(self) -> AppUser:
        """Возвращает объект пользователя по pk и запускает объектные permissions (IsSelf)."""
        # Вариант ***self.kwargs.get("pk")*** используется, если метод не принимает pk как параметр напрямую (например,
        # во вспомогательных методах вроде ***get_object()***. Там у нас нет переменной pk, и нужно лезть в kwargs.
        # ПОЭТОМУ:
        # 1) Внутри ***retrieve*** или ***partial_update*** логичнее писать pk=pk - это проще и понятнее для чтения.
        # 2) Внутри вспомогательных методов ***get_object()*** нужно так ***self.kwargs.get("pk")***, потому что
        # метод не принимает pk как аргумент.
        user = get_object_or_404(AppUser, pk=self.kwargs.get("pk"))
        # check_object_permissions() - это критически важно для срабатывания IsSelf.has_object_permission:
        self.check_object_permissions(self.request, user)
        return user

    def create(self, request):
        """Создает/регистрирует нового пользователя в приложении."""
        serializer = AppUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Получает данные одного пользователя по ID (доступно только владельцу профиля)."""
        user = self.get_object()  # Тут сработает IsSelf()
        serializer = AppUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        """Частично обновляет пользователя по ID (доступно только владельцу профиля)."""
        user = self.get_object()  # Тут сработает IsSelf()
        # Когда используется partial_update, то нужно указать partial=True, иначе будут валидироваться все поля!
        serializer = AppUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def user_set_password(self, request, pk=None):
        """Смена пароля текущего пользователя."""
        user = self.get_object()

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response({"detail": "Оба поля обязательны (old / new)."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({"detail": "Старый пароль неверен."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Пароль успешно изменён."}, status=status.HTTP_200_OK)


class UserTokenObtainPairView(TokenObtainPairView):
    """Класс-контроллер на основе TokenObtainPairView для авторизации по email."""

    permission_classes = [AllowAny]  # type: ignore[assignment]
    serializer_class = UserObtainPairSerializer
