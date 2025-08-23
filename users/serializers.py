from rest_framework import serializers
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import AppUser


class AppUserSerializer(serializers.ModelSerializer):
    """Класс-сериализатор с использованием класса ModelSerializer для осуществления базовой сериализация в DRF на
    основе модели AppUser. Описывает то, какие поля модели AppUser будут участвовать в сериализации и
    десериализации."""

    def create(self, validated_data):
        """Переопределяет создание пользователя, чтобы пароль сохранялся БД в хэшированном виде."""
        password = validated_data.pop("password")
        user = AppUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, obj, validated_data):
        """Полностью блокирует password в методе update, чтоб пароль менялся только через реализованный
        специально для этого метод user_set_password с хешированием."""
        if "password" in validated_data:
            raise serializers.ValidationError(
                {"password": "Пароль нельзя изменять через update. Используйте существующий метод смены пароля."}
            )
        return super().update(obj, validated_data)

    class Meta:
        model = AppUser
        # # Лучше не использовать fields = "__all__" потому что с "__all__" наш API отдаст все поля,
        # # включая is_staff, is_superuser, groups и т.п. Это опасно, потому что через API можно будет
        # # назначить себе суперправа.
        # fields = ("id", "email", "first_name", "last_name", "phone_number", "city", "avatar", "password")
        fields = "__all__"
        # extra_kwargs - это зарезервированное имя в Meta-классе ModelSerializer для настройки конкретных полей,
        # например, ниже указываю что пароль только на ЗАПИСЬ. Т.е. его можно отправить через POST/PUT/PATCH,
        # но оно не будет отображаться в ответе API (GET, LIST и т.п.).
        extra_kwargs = {
            "password": {"write_only": True},
        }


class UserObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный класс-сериализатор токена наследующийся от TokenObtainPairSerializer, позволяющий вход по email."""

    # ВАЖНО! Необходимо указать, что username_field - это будет email.
    # До это мы указывали в модели это "USERNAME_FIELD = "email"" но это настройка Django, например, в админке,
    # логике логина, командах createsuperuser и т.п. Но это не влияет на процессы DRF. Логика сериализатора от
    # DRF Simple JWT НЕ смотрит на USERNAME_FIELD модели автоматически. Поэтому чтобы Simple JWT понял, что логин
    # должен быть по email, а не по username, нужно явно указать это в сериализаторе в username_field
    username_field = AppUser.EMAIL_FIELD

    def validate(self, attrs):
        """Валидация данных при получении токена: проверка существования пользователя и корректности пароля."""
        # Получаю email и password из тела запроса
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:  # ШАГ 1: проверяю все ли данные есть
            try:  # ШАГ 2: Ищу пользователя с таким email
                user = AppUser.objects.get(email=email)
            except AppUser.DoesNotExist:
                raise AuthenticationFailed("Пользователь с таким email не найден.")

            if not user.check_password(password):  # ШАГ 3: Проверяю пароль
                raise AuthenticationFailed("Неверный пароль.")

        else:
            raise AuthenticationFailed("Необходимо указать email и пароль.")

        # ШАГ 4: Если все ок, то формирую словарь, чтобы передать в родительский "validate()"
        data = super().validate(
            {
                self.username_field: user.email,  # Ключ "email", значение - email пользователя
                "password": password,
            }
        )
        # ШАГ 5: Добавляю еще данные в ответ (опционально, это полезно для будущего функционала)
        data["email"] = user.email
        data["user_id"] = user.id

        return data
