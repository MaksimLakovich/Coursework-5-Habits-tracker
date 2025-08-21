from rest_framework import serializers

from users.models import AppUser


class AppUserSerializer(serializers.ModelSerializer):
    """Класс-сериализатор с использованием класса ModelSerializer для осуществления базовой сериализация в DRF на
    основе модели AppUser. Описывает то, какие поля модели AppUser будут участвовать в сериализации и
    десериализации."""

    def create(self, validated_data):
        """Переопределяем создание пользователя, чтобы пароль сохранялся БД в хэшированном виде."""
        password = validated_data.pop("password")
        user = AppUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

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
