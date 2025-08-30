from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import AppUser


class UsersAPITestCase(APITestCase):
    """Тесты, которые будут проверять работу CRUD для пользователей (AppUser)."""

    def setUp(self):
        """Метод для подготовки тестовых данных и настроек перед выполнением тестов в тестовом классе."""
        self.user = AppUser.objects.create_user(
            email="user_1@gmai.com",
            password="123qwe",
        )
        self.stranger = AppUser.objects.create_user(
            email="user_2@gmai.com",
            password="456rty",
        )
        # Авторизую основного пользователя
        self.client.force_authenticate(user=self.user)

    def test_create_user(self):
        """Регистрация нового пользователя (POST-запрос)."""
        url = reverse("users:user-register")
        data = {
            "email": "new_user@gmai.com",
            "password": "123qwe",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AppUser.objects.count(), 3)
        self.assertTrue(AppUser.objects.filter(email="new_user@gmai.com").exists())

    def test_get_own_profile(self):
        """Просмотр собственного профиля (GET)."""
        url = reverse("users:user-detail", args=[self.user.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_update_own_profile(self):
        """Обновление собственного профиля (PATCH)."""
        url = reverse("users:user-update", args=[self.user.pk])
        new_data = {
            "email": "user_1_new_email@gmai.com",
        }

        response = self.client.patch(url, new_data, format="json")

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, "user_1_new_email@gmai.com")

    def test_403_forbidden_update_other_user(self):
        """Попытка редактирования чужого профиля (403)."""
        url = reverse("users:user-update", args=[self.stranger.pk])
        new_data = {
            "email": "user_2_new_email@gmai.com",
        }

        response = self.client.patch(url, new_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login(self):
        """Проверка входа (получение JWT токенов)."""
        url = reverse("users:login")
        data = {
            "email": "user_2@gmai.com",
            "password": "456rty",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_set_password_success(self):
        """Успешная смена пароля самим пользователем."""
        url = reverse("users:user-set-password", args=[self.user.pk])
        data = {
            "old_password": "123qwe",
            "new_password": "newpassword123",
        }

        response = self.client.post(url, data, format="json")

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password("newpassword123"))

    def test_set_password_forbidden(self):
        """Попытка сменить пароль чужому пользователю (403)."""
        url = reverse("users:user-set-password", args=[self.stranger.pk])
        data = {
            "new_password": "newpassword123",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_set_password_unauthenticated(self):
        """Неавторизованный пользователь не может менять пароли (401)."""
        self.client.logout()  # Разлогиниваю пользователя
        url = reverse("users:user-set-password", args=[self.user.pk])
        data = {
            "new_password": "newpassword123",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
