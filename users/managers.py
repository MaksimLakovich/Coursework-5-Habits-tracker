from django.contrib.auth.models import BaseUserManager


class AppUserManager(BaseUserManager):
    """Кастомный менеджер для создания пользователя без поля username."""

    def create_user(self, email, password=None, **extra_fields):
        """Создает и возвращает обычного пользователя."""
        if not email:
            raise ValueError("Email обязателен для создания пользователя")

        if not password:
            raise ValueError("Пароль обязателен для создания пользователя")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создает и возвращает суперпользователя."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")
        return self.create_user(email, password, **extra_fields)
