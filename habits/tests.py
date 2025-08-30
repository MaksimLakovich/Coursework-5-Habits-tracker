from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habits
from users.models import AppUser


class HabitsCRUDAPITestCase(APITestCase):
    """Тесты, которые будут проверять работу CRUD для привычек (Habits)."""

    def setUp(self):
        """Метод для подготовки тестовых данных и настроек перед выполнением тестов в тестовом классе."""
        # ШАГ 1: Создаю тестовых пользователей.
        # Нужно 2 users для проверки различных прав доступов - IsOwner, IsSelf.
        self.user = AppUser.objects.create_user(
            email="user_1@gmai.com",
            password="123qwe",
        )
        self.stranger = AppUser.objects.create_user(
            email="user_2@gmai.com",
            password="456qwe",
        )
        # Сразу же выполняю аутентификацию под основным тестовым пользователем, чтоб исключить *401 Unauthorized*, так
        # как в настройках (settings.py): 'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated']
        self.client.force_authenticate(user=self.user)

        # ШАГ 2: Создаю тестовые привычки.
        # 2.1. Приятную привычку под USER, чтоб использовать ее потом в тестах для related_pleasant_habit, а также
        # работы вьюх со списками и прав доступа
        # 2.2. Привычку под STRANGER, чтоб проверять потом работу вьюх со списками и прав доступа
        self.pleasant_habit = Habits.objects.create(
            owner=self.user,
            description="Купить двойной МакМафин по пути в офис",
            location="МакДональдс",
            time="8:30",
            is_pleasant=True,
            periodicity=1,
            related_pleasant_habit=None,
            reward=None,
            time_to_complete=120,
            is_public=True,
        )
        self.habit_by_stranger = Habits.objects.create(
            owner=self.stranger,
            description="Почитать книгу в слух перед сном",
            location="дом",
            time="22:30",
            is_pleasant=False,
            periodicity=1,
            related_pleasant_habit=None,
            reward="Съесть сникерс",
            time_to_complete=120,
            is_public=False,
        )

    def test_create_habit(self):
        """Создание новой полезной привычки (POST-запрос)."""
        url = reverse("habits:habit-create")
        data = {
            "owner": self.user.pk,
            "description": "Утренняя пробежка",
            "location": "парк возле дома",
            "time": "7:00",
            "is_pleasant": False,
            "periodicity": 1,
            "related_pleasant_habit": self.pleasant_habit.pk,
            "reward": None,
            "time_to_complete": 120,
            "is_public": False,
        }

        response = self.client.post(url, data, format="json")
        created_habit = Habits.objects.get(description=data["description"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habits.objects.count(), 3)
        self.assertEqual(created_habit.description, data["description"])
        self.assertEqual(created_habit.related_pleasant_habit, self.pleasant_habit)
        self.assertEqual(created_habit.owner, self.user)

    def test_list_user_habits(self):
        """Получить список привычек пользователя (GET-запрос)."""
        url = reverse("habits:habits-user-list")
        Habits.objects.create(
            owner=self.user,
            description="Утренняя пробежка",
            location="парк возле дома",
            time="7:00",
            is_pleasant=False,
            periodicity=1,
            related_pleasant_habit=self.pleasant_habit,
            reward=None,
            time_to_complete=120,
            is_public=False,
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Habits.objects.all().count(), 3)
        # Проверяю содержимое в списке и из-за того, что есть пагинация появляется "results".
        # Без пагинации было бы просто: response.data[0]["description"].
        self.assertEqual(len(response.data["results"]), 2)
        all_descriptions = [habit["description"] for habit in response.data["results"]]
        self.assertIn("Купить двойной МакМафин по пути в офис", all_descriptions)
        self.assertIn("Утренняя пробежка", all_descriptions)

    def test_list_public_habits(self):
        """Получить список всех публичных привычек (GET-запрос)."""
        url = reverse("habits:habits-public-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Habits.objects.all().count(), 2)
        self.assertEqual(Habits.objects.filter(is_public=True).count(), 1)

    def test_update_habit(self):
        """Обновить существующую привычку (PATCH-запрос)."""
        existed_habit = Habits.objects.get(description="Купить двойной МакМафин по пути в офис")
        new_data = {
            "is_public": True,
            "reward": "Поиграть в комп игру"
        }
        url = reverse("habits:habit-detail", args=[existed_habit.pk])

        response = self.client.patch(url, new_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_public"], True)

    def test_delete_habit(self):
        """Удалить существующую привычку (DELETE-запрос)."""
        existed_habit = Habits.objects.get(description="Купить двойной МакМафин по пути в офис")
        url = reverse("habits:habit-detail", args=[existed_habit.pk])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habits.objects.all().count(), 1)

    def test_401_unauthenticated_get_list_public_habits(self):
        """Получение списка публичных привычек неавторизованным пользователем (401 - Unauthorized)."""
        self.client.logout()  # Разлогиниваю пользователя
        url = reverse("habits:habits-public-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Habits.objects.filter(is_public=True).count(), 1)

    def test_403_forbidden_update_habit_by_stranger(self):
        """Запрет редактирования чужих привычек (403 - Forbidden)."""
        existed_habit_by_stranger = Habits.objects.get(description="Почитать книгу в слух перед сном")
        new_data = {
            "is_public": True
        }
        url = reverse("habits:habit-detail", args=[existed_habit_by_stranger.pk])

        response = self.client.patch(url, new_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class HabitsValidatorsAPITestCase(APITestCase):
    """Тесты, которые будут проверять работу валидаторов для модели привычек (Habits)."""

    def setUp(self):
        self.user = AppUser.objects.create_user(
            email="user_1@gmai.com",
            password="123qwe",
        )
        self.client.force_authenticate(user=self.user)

        # Приятная привычка, которая будет использоваться как related_pleasant_habit
        self.pleasant_habit = Habits.objects.create(
            owner=self.user,
            description="Съесть мороженое после работы",
            location="кафе",
            time="19:00",
            is_pleasant=True,
            periodicity=1,
            related_pleasant_habit=None,
            reward=None,
            time_to_complete=60,
            is_public=False,
        )

    def test_cannot_set_both_reward_and_related_habit(self):
        """Нельзя указывать одновременно reward и related_pleasant_habit."""
        url = reverse("habits:habit-create")
        data = {
            "owner": self.user.pk,
            "description": "Пробежка утром",
            "location": "стадион",
            "time": "07:00",
            "is_pleasant": False,
            "periodicity": 1,
            "related_pleasant_habit": self.pleasant_habit.pk,
            "reward": "Съесть шоколадку",
            "time_to_complete": 100,
            "is_public": False,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_set_time_to_complete_more_than_120(self):
        """Нельзя указывать время выполнения больше 120 секунд."""
        url = reverse("habits:habit-create")
        data = {
            "owner": self.user.pk,
            "description": "Растяжка",
            "location": "зал",
            "time": "09:00",
            "is_pleasant": False,
            "periodicity": 1,
            "related_pleasant_habit": None,
            "reward": "купить сок",
            "time_to_complete": 300,  # превышение
            "is_public": True,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("time_to_complete", response.data)

    def test_cannot_set_reward_for_pleasant_habit(self):
        """Приятная привычка не может иметь вознаграждение."""
        url = reverse("habits:habit-create")
        data = {
            "owner": self.user.pk,
            "description": "Сходить в кино",
            "location": "кинотеатр",
            "time": "20:00",
            "is_pleasant": True,
            "periodicity": 1,
            "related_pleasant_habit": None,
            "reward": "купить попкорн",  # запрещено
            "time_to_complete": 90,
            "is_public": False,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_set_periodicity_more_than_once_a_day(self):
        """Нельзя создавать привычку с периодичностью чаще, чем 1 раз в день."""
        url = reverse("habits:habit-create")
        data = {
            "owner": self.user.pk,
            "description": "Пить воду каждый час",
            "location": "офис",
            "time": "10:00",
            "is_pleasant": False,
            "periodicity": 0,  # недопустимое значение (должно быть от 1 до 7)
            "related_pleasant_habit": None,
            "reward": None,
            "time_to_complete": 30,
            "is_public": True,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("periodicity", response.data)


class UserHabitsListPaginationAPITestCase(APITestCase):
    """Тесты, которые будут проверять работу пагинации списка привычек пользователя (Habits)."""

    def setUp(self):
        self.user = AppUser.objects.create_user(
            email="user_1@gmai.com",
            password="123qwe",
        )
        self.client.force_authenticate(user=self.user)

        # Создаю множество привычек. Чтоб было больше, чем размер страницы (page_size=5 по умолчанию)
        for i in range(7):
            Habits.objects.create(
                owner=self.user,
                description=f"Привычка №{i}",
                location="дом",
                time="08:00",
                is_pleasant=False,
                periodicity=1,
                related_pleasant_habit=None,
                reward=f"Награда №{i}",
                time_to_complete=60,
                is_public=True,
            )

    def test_first_page_contains_page_size_results(self):
        """Первая страница возвращает ровно page_size привычек."""
        url = reverse("habits:habits-user-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)  # page_size=5
        self.assertIn("next", response.data)  # есть ссылка на следующую страницу

    def test_second_page_contains_remaining_results(self):
        """Вторая страница возвращает остаток привычек."""
        url = reverse("habits:habits-user-list") + "?page=2"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)  # всего было 7, поэтому на третьей странице 2
        self.assertIn("previous", response.data)  # есть ссылка на вторую страницу
