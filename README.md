# HABITS TRACKER API (Django REST Framework)

---

[1. Цель проекта](#title1) / 
[2. Модели](#title2) / 
[3. Админки](#title3) / 
[4. Сериализация](#title4) / 
[5. Валидация](#title5) / 
[6. Контроллеры](#title6) / 
[7. Маршруты](#title7) / 
[8. Права доступов](#title8) / 
[9. Пагинация](#title9) / 
[10. Telegram-бот](#title10) / 
[11. Сервисные функции](#title11) / 
[12. Вспомогательные функции](#title12) / 
[13. Отложенные задачи](#title13) / 
[14. Тестирование приложения](#title14) / 
[15. Получение ключей .env](#title15) / 
[16. Получение ключей .env.docker.example](#title16) / 
[17. Описание файла .flake8](#title17) / 
[18. Описание файла mypy.ini](#title18) / 
[19. Описание файла .coveragerc](#title19) / 
[20. Документация к API](#title20) / 
[21. Установка проекта](#title21) / 
[22. Установка и запуск проекта на сервере (через Docker и Nginx)](#title22) / 
[23. Автоматический деплой через GitHub Actions](#title23) / 

---

# <a id="title1">1. Цель проекта</a>
Backend-часть SPA веб-приложения (трекер полезных привычек), которое посвящено работе по приобретению новых полезных привычек и искоренению старых плохих привычек.
Разработка выполнена над SPA веб-приложением и результатом проекта является бэкенд-сервер, который возвращает клиенту JSON-структуры.

Проект включает следующие приложения:
- Users
- Habits
- Telegram_bot

---

# <a id="title2">2. Описание моделей (models)</a>

## _Приложение "Users" (users/models.py):_

1) Модель данных `AppUser(AbstractUser)` - представляет Пользователя в приложении (авторизация по email).
   - Наследуется от модели **AbstractUser**, которая является готовой моделью и включает все основные поля и методы, такие как username, email, first_name, last_name, is_staff, is_active и другие.
   - ***Дополнительно определено:***
     - ник пользователя (username);
     - эл.почта пользователя (email);
     - телефон пользователя (phone_number);
     - город пользователя (city);
     - аватар пользователя (avatar).

## _Приложение "Habits" (habits/models.py):_

1) Абстрактная базовая модель `TimeStampedModel(models.Model)` - для дальнейшего создания *created_at* и *updated_at* во всех моделях приложения, где она будет использоваться:
   - *Поля модели:*
     - дата создания (created_at).
     - дата обновления (updated_at).

2) Модель данных `Habits(TimeStampedModel)` - представляет привычку пользователя в приложении:
   - *Наследование:*
     - наследуется от абстрактной базовой модели ***TimeStampedModel*** для добавления *created_at* и *updated_at* по умолчанию.
   - *Поля модели:*
     - Владелец (owner).
     - Место (location).
     - Время (time).
     - Действие (description).
     - Признак приятной привычки (is_pleasant).
     - Связанная приятная привычка (related_pleasant_habit).
     - Периодичность (periodicity).
     - Вознаграждение (reward).
     - Время на выполнение (time_to_complete).
     - Признак публичности (is_public).

## _Приложение "Telegram_bot" (telegram_bot/models.py):_

1) Модель данных `TelegramProfile(TimeStampedModel)` - представляет телеграм-профиль пользователя в приложении:
   - *Наследование:*
     - наследуется от абстрактной базовой модели ***TimeStampedModel*** для добавления *created_at* и *updated_at* по умолчанию.
   - *Поля модели:*
     - Пользователь приложения (app_user).
     - Telegram ChatID (telegram_chat_id).
     - Telegram UserID (telegram_user_id).

---

# <a id="title3">3. Описание админок (admin)</a>

## _Приложение "Users" (users/admin.py):_

1) Админка `AppUserAdmin(UserAdmin)` - отображение данных модели *AppUser* (Пользователь) в админке.

## _Приложение "Habits" (habits/admin.py):_

1) Админка `HabitsAdmin(admin.ModelAdmin)` - отображение данных модели *Habits* (Привычка) в админке.

## _Приложение "Telegram_bot" (telegram_bot/models.py):_

1) Админка `TelegramProfileAdmin(admin.ModelAdmin)` - отображение данных модели *TelegramProfile* (Телеграм-профиль) в админке.

---

# <a id="title4">4. Описание сериализаторов (serializers)</a>

## _Приложение "Users" (users/serializers.py):_

1) `AppUserSerializer(serializers.ModelSerializer)` - класс-сериализатор с использованием класса **ModelSerializer** для осуществления базовой сериализация в DRF на основе модели *AppUser*. Описывает то, какие поля модели *AppUser* будут участвовать в сериализации и десериализации.
   - Кастомизация сериализатора:
     - `create(self, validated_data)` - переопределение метода создания пользователя, чтобы пароль сохранялся БД в хэшированном виде.
     - `update(self, obj, validated_data)` - полностью блокирует *password* в методе **update**, чтоб пароль менялся только через реализованный специально для этого метод **user_set_password** с хешированием.
   - Дополнительные параметры *Meta-класса*:
     - параметр `extra_kwargs` - зарезервированное имя параметра в Meta-классе **ModelSerializer** для настройки конкретных полей, например, ниже указываю что пароль только на ЗАПИСЬ. Т.е. его можно отправить через POST/PUT/PATCH, но он не будет отображаться в ответе API (GET, LIST и т.п.).
     ``` python
     extra_kwargs = {
        "password": {"write_only": True},
     }
     ```
2) `UserObtainPairSerializer(TokenObtainPairSerializer)` - класс-сериализатор токена наследующийся от **TokenObtainPairSerializer** для входа/авторизации по email.
    - Кастомизация сериализатора:
      - `validate(self, attrs)` - валидация данных при получении токена: проверка существования пользователя и корректности пароля.

## _Приложение "Habits" (habits/serializers.py):_

1) `HabitsSerializer(serializers.ModelSerializer)` - класс-сериализатор с использованием класса *ModelSerializer* для осуществления базовой сериализация в DRF на основе модели *Habits*. Описывает то, какие поля модели *Habits* будут участвовать в сериализации и десериализации.
   - Валидация:
     - Внутренняя валидация в самом сериализаторе:
       - `validate_time_to_complete(self, value)` - кастомная валидация поля *time_to_complete*, что привычка должна выполняться в допустимом (заданном) диапазоне.
       - `validate_periodicity(self, value)` - кастомная валидация поля *periodicity*: привычка должна выполняться хотя бы 1 раз в 7 дней.
       - `to_representation(self, instance)` - метод скрывает приватные данные других пользователей (*location*, *owner*) у публичных привычек.
     - Подключенные сторонние кастомные валидаторы:
       - `HabitRewardChoiceValidator`
       - `RelatedHabitPleasantValidator`
       - `PleasantHabitRestrictionsValidator`

---

# <a id="title5">5. Описание валидации (validators)</a>

## _Приложение ""Habits" (habits/validators.py):_

1) Класс-валидатор `HabitRewardChoiceValidator` - для проверок:
    1) что в ***полезной привычке***:
        - нельзя одновременно указать *связанную привычку* (related_pleasant_habit) и *вознаграждение* (reward);
        - должно быть указано хотя бы одно из двух полей.
    2) что в ***приятной привычке***:
        - нельзя указывать ни *вознаграждение* (reward), ни *связанную привычки* (related_pleasant_habit).

2) Класс-валидатор `RelatedHabitPleasantValidator` - для проверки, что в связанные привычки могут попадать только привычки с признаком приятной.

3) Класс-валидатор `PleasantHabitRestrictionsValidator` - для проверки, что у приятной привычки не может быть вознаграждения или связанной привычки.

---

# <a id="title6">6. Описание контроллеров (views)</a>

## _Приложение "Users" (users/views.py):_

1) Класс-контроллер `UserViewSetAPIView(viewsets.ViewSet)` - для создания, просмотра и редактирования пользователя в приложении:
   - на основе ***viewsets***.
   - методы:
     - `get_permissions(self)`: определяет права доступа в зависимости от действия:
       - create;
       - retrieve;
       - partial_update;
       - user_set_password.
     - `get_object(self)`: возвращает объект пользователя по pk и запускает объектные permissions (без этого не запустится во **viewsets.ViewSet** кастомный пермишен ***IsSelf***).
     - `create(self, request)`: создает/регистрирует нового пользователя в приложении (***POST***, ***status=201***).
     - `retrieve(self, request, pk=None)`: получает данные одного пользователя по ID (доступно только владельцу профиля) (***GET***, ***status=200***).
     - `partial_update(self, request, pk=None)`: частично обновляет пользователя по ID (доступно только владельцу профиля) (***PATCH***, ***status=200***).
     - `user_set_password(self, request, pk=None)`: смена пароля текущего пользователя (***POST***, ***status=200***).

2) Класс-контроллер `UserTokenObtainPairView(TokenObtainPairView)` - класс-контроллер на основе TokenObtainPairView для возможности авторизации по email, так как я убрал username, которое было по умолчанию в DRF.
   - на основе ***TokenObtainPairView*** - базовый класс для получения JWT-токена.

## _Приложение "Habits" (habits/views.py):_

1) Класс-контроллер `HabitsCreateAPIView(generics.CreateAPIView)` - для создания новой привычки в приложении:
   - на основе ***generics***.
   - методы:
     - `perform_create(self, serializer)`: метод:
       - присваивает текущего авторизованного пользователя как владельца (owner) создаваемого объекта.
       - запускает отложенную задачу по отправке напоминания о необходимости выполнения полезной привычки:
         - параметр ***countdown*** для функции запуска отложенной задачи рассчитывается индивидуально для каждой привычки через сервисную функцию set_param_countdown().

2) Класс-контроллер `UserHabitsListAPIView(generics.ListAPIView)` - для получения списка привычек текущего пользователя:
   - на основе ***generics***.
   - методы:
     - `get_queryset(self)`: получение набора данных, который будет использоваться во View.
   - пагинация страницы:
     - `pagination_class = UserHabitsListPagination`

3) Класс-контроллер `PublicHabitsListAPIView(generics.ListAPIView)` - для получения списка публичных привычек:
   - на основе ***generics***.
   - методы:
     - `get_queryset(self)`: получение набора данных, который будет использоваться во View.
   - пагинация страницы:
     - `pagination_class = PublicHabitsListPagination`

4) Класс-контроллер `HabitsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView)` - для просмотра, обновления и удаления конкретной привычки:
   - на основе ***generics***.
   - валидация:
     - `permission_classes = [IsOwner]`: пользователь имеет доступ только к своим привычкам по механизму CRUD.
   - методы:
     - `perform_update(self, serializer)`: запускает отложенную задачу по отправке напоминания о необходимости выполнения полезной привычки:
       - параметр ***countdown*** для функции запуска отложенной задачи рассчитывается индивидуально для каждой привычки через сервисную функцию set_param_countdown().

## _Приложение "Telegram_bot" (telegram_bot/urls.py):_

1) Класс-контроллер `TelegramConnectAPIView(APIView)` - API-эндпоинт для привязки Telegram-аккаунта к пользователю нашего приложения:
   - когда пользователь в Telegram-боте вводит команду ***/start***, бот берёт *chat_id* и *user_id* из Telegram API и отправляет их POST-запросом на этот эндпоинт "/api/telegram/connect/" добавляя в заголовок авторизационный токен пользователя из приложения.
   - здесь для авторизованного пользователя создаётся или обновляется модель "TelegramProfile", чтобы мы знали, в какой чат отправлять напоминания о привычках.
- на основе базового ***APIView***.
- методы:
  - `post(self, request)`: Обрабатывает POST-запрос от Telegram-бота.
    - Ожидает в теле запроса:
      - "telegram_chat_id": ID чата Telegram, куда будут приходить напоминания;
      - "telegram_user_id": уникальный ID пользователя в Telegram.
    - Действия метода:
      - Проверяет наличие "telegram_chat_id" в запросе.
      - Использует "update_or_create", чтобы либо создать новый "TelegramProfile" для текущего пользователя приложения, либо обновить существующий.
    - Возвращает JSON-ответ с результатом:
      - "created=True" - профиль был создан;
      - "created=False" - профиль уже существовал и был обновлён.

---

# <a id="title7"7. Описание маршрутов (urls)</a>

## _Приложение "Users" (users/urls.py):_

```python
urlpatterns = [
    path("login/", UserTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", UserViewSetAPIView.as_view({"post": "create"}), name="user-register"),
    path("users/<int:pk>/", UserViewSetAPIView.as_view({"get": "retrieve"}), name="user-detail"),
    path("users/<int:pk>/update/", UserViewSetAPIView.as_view({"patch": "partial_update"}), name="user-update"),
    path("users/<int:pk>/set_password/", UserViewSetAPIView.as_view({"post": "user_set_password"}), name="user-set-password"),
]
```

## _Приложение "Habits" (habits/urls.py):_

```python
urlpatterns = [
    path("habits/", HabitsCreateAPIView.as_view(), name="habit-create"),
    path("habits/user/", UserHabitsListAPIView.as_view(), name="habits-user-list"),
    path("habits/public/", PublicHabitsListAPIView.as_view(), name="habits-public-list"),
    path("habits/<int:pk>/", HabitsRetrieveUpdateDestroyAPIView.as_view(), name="habit-detail"),
]
```

## _Приложение "Telegram_bot" (telegram_bot/urls.py):_

```python
urlpatterns = [
    path("telegram/connect/", TelegramConnectAPIView.as_view(), name="telegram-connect"),
]
```

---

# <a id="title8">8. Описание прав доступов (permissions)</a>

## _Приложение "Users" (users/permissions.py):_

1) Класс `IsSelf(BasePermission)` - кастомный permission-класс, который разрешает доступ только владельцу своего профиля.

## _Приложение "Habits" (habits/permissions.py):_

1) Класс `IsOwner(BasePermission)` - кастомный permission-класс, который проверяет, является ли пользователь владельцем (owner) объекта.

---

# <a id="title9">9. Описание пагинации (paginators)</a>

## _Приложение "Habits" (habits/paginators.py):_

1) Класс `BaseHabitsListPagination(PageNumberPagination)` - базовый класс с общими настройками пагинации для страниц со списками от которого буду потом наследоваться в:
   - `UserHabitsListPagination(BaseHabitsListPagination)`: вывод по 5 привычек на странице ***/habits/user/***.
   - `PublicHabitsListPagination(BaseHabitsListPagination)`: вывод по 10 привычек на странице ***/habits/public/***.

---

# <a id="title10">10. Описание Telegram-бота</a>
 
## _Приложение "Telegram_bot" (telegram_bot/bot.py):_

Простой Telegram-бот (*aiogram v3*) для привязки Telegram-чата к аккаунту в Django-приложении.

**Основная идея:**
- бот помогает пользователю получить JWT-токены от Django (через /login), сохранить refresh токен для него локально, 
а затем при /start бот берет refresh, получает новый access и вызывает твой Django-эндпоинт /api/telegram/connect/, чтобы связать telegram_chat_id 
с аккаунтом в приложении.

**Функционал:**
- /login - интерактивно просит email и пароль, получает access/refresh у Django и сохраняет refresh локально;
- /start  - если есть сохранённый refresh, бот запрашивает новый access, вызывает Django
             эндпоинт /api/telegram/connect/ и тем самым привязывает telegram_chat_id к пользователю.

**ВАЖНО:**
- Используется локальное хранилище в telegram_bot/data/creds.json (подходит только для разработки).
- Переменные окружения грузятся из .env (через python-dotenv).

**Команды бота:**
- `/help` - справка с доступными командами.
- `/login` - команда инициирует диалог с пользователем для его авторизации:
  - Бот просит email, переходит в состояние waiting_email.
  - Получает email от пользователя, сохраняет во временное состояние и просит пароль.
  - Получает пароль, делает запрос к Django /api/login/ и при успехе сохраняет refresh локально.
- `/start` - бот:
  - получает сохранённый refresh по telegram user id.
  - обновляет access
  - вызывает Django API /api/telegram/connect/ чтобы привязать telegram_chat_id к пользователю.

---

# <a id="title11">11. Описание сервисных функций (services)</a>

## _Приложение "Habits" (habits/services.py):_

1) Функция `set_param_countdown(habit)` - сервисная функция для определения значения параметра ***countdown*** для каждой привычки, чтоб отправлять уведомление согласно настроек в *REMINDER_OFFSET_MINUTES* (например, за 30 мин до).
   - ***:param habit***: привычка (объект).
   - 
## _Приложение "Telegram_bot" (telegram_bot/services.py):_

1) Функция `send_telegram_message(chat_id, message)` - сервисная функция для отправки сообщения пользователю в Telegram:
   - ***:param chat_id***: Telegram ChatID пользователя.
   - ***:param message***: Текст сообщения в Telegram.

---

# <a id="title12">12. Вспомогательные функции</a>

## _Приложение "Users" (users/managers.py):_

1) Класс `AppUserManager(BaseUserManager)` - кастомный менеджер для пользователя без поля username:
   - функция `create_user()` - создает и возвращает обычного пользователя.
   - функция `create_superuser()` - создает и возвращает суперпользователя.

---

# <a id="title13">13. Отложенные задачи</a>

## _Приложение "Telegram_bot" (telegram_bot/tasks.py):_

1) Отложенная задача `task_send_reminding_message(self, habit_id)` - напоминает пользователю о необходимости выполнения полезной привычки. Учитывается периодичность выполнения привычки:
   - ***:param habit_id*** - ID привычки, для которой нужно отправить напоминание.
   - ***@shared_task(bind=True, max_retries=3)*** - устанавливает количество попыток отправки, если предыдущая отправка не сработала.

1) Периодическая задача `task_send_daily_message()` - каждый день в установленное время отправляет пользователю полный список его привычек к исполнению на сегодня.

---

# <a id="title14">14. Тестирование приложения</a>

Команда для запуска тестов:
```commandline
python3 manage.py test --keepdb
```

Команды для проверки уровня покрытия тестами:
   ```commandline
   coverage erase
   coverage run manage.py test --keepdb
   coverage report -m
   ```

## _Приложение "Users" (users/views.py):_

1) Класс `(UsersAPITestCase)` - тесты, которые будут проверять работу CRUD для пользователей (AppUser):
  - `test_create_user` - регистрация нового пользователя (POST-запрос).
  - `test_get_own_profile` - просмотр собственного профиля (GET).
  - `test_update_own_profile` - обновление собственного профиля (PATCH).
  - `test_403_forbidden_update_other_user` - попытка редактирования чужого профиля (403).
  - `test_login` - проверка входа (получение JWT токенов).
  - `test_set_password_success` - успешная смена пароля самим пользователем.
  - `test_set_password_forbidden` - попытка сменить пароль чужому пользователю (403).
  - `test_set_password_unauthenticated` - неавторизованный пользователь не может менять пароли (401).

## _Приложение "Habits" (habits/tests.py):_

1) Класс `HabitsCRUDAPITestCase(APITestCase)` - тесты, которые будут проверять работу ***CRUD*** для привычек (Habits):
   - `test_create_habit` - создание новой полезной привычки (POST-запрос).
   - `test_list_user_habits` - получить список привычек пользователя (GET-запрос).
   - `test_list_public_habits` - получить список всех публичных привычек (GET-запрос).
   - `test_update_habit` - обновить существующую привычку (PATCH-запрос).
   - `test_delete_habit` - удалить существующую привычку (DELETE-запрос).
   - `test_401_unauthenticated_get_list_public_habits` - получение списка публичных привычек неавторизованным пользователем (401 - Unauthorized).
   - `test_403_forbidden_update_habit_by_stranger` - запрет редактирования чужих привычек (403 - Forbidden).

2) Класс `HabitsValidatorsAPITestCase(APITestCase)` - тесты, которые будут проверять работу ***валидаторов*** для модели привычек (Habits):
   - `test_cannot_set_both_reward_and_related_habit` - нельзя указывать одновременно reward и related_pleasant_habit.
   - `test_cannot_set_time_to_complete_more_than_120` - нельзя указывать время выполнения больше 120 секунд.
   - `test_cannot_set_reward_for_pleasant_habit` - приятная привычка не может иметь вознаграждение.
   - `test_cannot_set_periodicity_more_than_once_a_day` - нельзя создавать привычку с периодичностью чаще, чем 1 раз в день.

3) Класс `UserHabitsListPaginationAPITestCase(APITestCase)` - тесты, которые будут проверять работу ***пагинации*** списка привычек пользователя (Habits):
  - `test_first_page_contains_page_size_results` - первая страница возвращает ровно page_size привычек.
  - `test_second_page_contains_remaining_results` - вторая страница возвращает остаток привычек.

## _Приложение "Telegram_bot" (telegram_bot/tests.py):_

1) Класс `TelegramBotServicesTests(TestCase)` - тесты, которые будут проверять работу ***сервисов*** Telegram-бота:
   - `test_send_telegram_message(self, mock_get)` - тест, что сервисная функция send_telegram_message() вызывает requests.get с правильными параметрами.

---
    
# <a id="title15">15. Получение ключей. Описание файла .env.example</a> 
1. Создайте файл .env в корне проекта из копии подготовленного файла `.env.example`, в котором описаны названия всех переменных, необходимых для работы приложения.
2. Замените значения переменных реальными данными.
3. Файл должен содержать данные:
```dotenv
# Настройки секретного ключа проекта django в config/settings.py
#Django рекомендует в целях безопасности хранить секретный ключ, используемый в продакшене, в тайне!
SECRET_KEY_FOR_PROJECT=secret_key_here

# Настройки дебага. В settings.py дебаг должен быть описан так: DEBUG = True if os.getenv('DEBUG') == 'True' else False
DEBUG=

# Настройки БД проекта django в config/settings.py
DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=
DATABASE_PORT=

# Это базовый вариант (разные БД Redis под брокера и результаты).
# Но, если хочется проще, то можно один и тот же (/0) использовать, но на проде лучше разделять!
# 1) URL-адрес брокера сообщений (Redis)
CELERY_BROKER_URL=
# 2) URL-адрес брокера результатов - хранилище результатов выполнения задаx (использую тот же Redis)
CELERY_RESULT_BACKEND=

# Настройки для Telegram-бота (токен)
TELEGRAM_BOT_TOKEN=
# 1) ЧТО ЭТО?
# Если используется нестандартный порт (например, http://127.0.0.1:8081/admin/ вместо http://127.0.0.1:8000/admin/),
# то Django будет не доверять адресу http://127.0.0.1:8081/admin/, так как источник будет не совпадать с
# доверенным доменом из ALLOWED_HOSTS или CSRF_TRUSTED_ORIGINS и выдаст 403 CSRF verification failed.
# Чтоб исключить ошибку нужно добавить параметр CSRF_TRUSTED_ORIGINS в settings.py и указывать в нем список
# доверенных доменов с портами
# 2) ДОП ПОЯСНЕНИЕ:
# Django проверяет конфигурацию, и в CSRF_TRUSTED_ORIGINS должен быть СПИСОК и без пустых некорректных
# данных, поэтому если не хардкодить тут и выносить в .ENV , то нужно писать код для создания списка без пустых
# значений в конце.
CSRF_TRUSTED_ORIGINS=http://хост:8081,http://localhost:3000
```

---

# <a id="title16">16. Получение ключей. Описание файла .env.docker.example</a> 
1. Создайте файл .env.docker в корне проекта из копии подготовленного файла `.env.docker.example`, в котором описаны названия всех переменных, необходимых для работы приложения.
2. Замените значения переменных реальными данными.
3. Файл должен содержать данные:
```dotenv
# Настройки секретного ключа проекта django в config/settings.py
#Django рекомендует в целях безопасности хранить секретный ключ, используемый в продакшене, в тайне!
SECRET_KEY_FOR_PROJECT=secret_key_here

# Настройки дебага. В settings.py дебаг должен быть описан так: DEBUG = True if os.getenv('DEBUG') == 'True' else False
DEBUG=

# Настройки БД (ВАЖНО!!! В Docker DATABASE_HOST = db)
# Название базы для приложения:
# 1) Postgres (для контейнера db)
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

# 2) Django (чтобы settings.py подхватывал те же значения)
DATABASE_NAME="${POSTGRES_DB}"
DATABASE_USER="${POSTGRES_USER}"
DATABASE_PASSWORD="${POSTGRES_PASSWORD}"
DATABASE_HOST=db
DATABASE_PORT=


# Это базовый вариант (разные БД Redis под брокера и результаты).
# Но, если хочется проще, то можно один и тот же (/0) использовать, но на проде лучше разделять!
# 1) URL-адрес брокера сообщений (Redis) (ВАЖНО!!! В Docker Redis = redis)
CELERY_BROKER_URL=redis://redis:6379/0
# 2) URL-адрес брокера результатов - хранилище результатов выполнения задач (ВАЖНО!!! В Docker Redis = redis)
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Настройки для Telegram-бота (токен)
TELEGRAM_BOT_TOKEN=

# Имя пользователя DockerHub с которым связан наш репозитория проекта на GitHub через настройки секретного ключа там
DOCKER_HUB_USERNAME=
# 1) ЧТО ЭТО?
# Если используется нестандартный порт (например, http://127.0.0.1:8081/admin/ вместо http://127.0.0.1:8000/admin/),
# то Django будет не доверять адресу http://127.0.0.1:8081/admin/, так как источник будет не совпадать с
# доверенным доменом из ALLOWED_HOSTS или CSRF_TRUSTED_ORIGINS и выдаст 403 CSRF verification failed.
# Чтоб исключить ошибку нужно добавить параметр CSRF_TRUSTED_ORIGINS в settings.py и указывать в нем список
# доверенных доменов с портами
# 2) ДОП ПОЯСНЕНИЕ:
# Django проверяет конфигурацию, и в CSRF_TRUSTED_ORIGINS должен быть СПИСОК и без пустых некорректных
# данных, поэтому если не хардкодить тут и выносить в .ENV , то нужно писать код для создания списка без пустых
# значений в конце.
CSRF_TRUSTED_ORIGINS=http://хост:8081,http://localhost:3000
```

---

# <a id="title17">17. Описание файла .flake8</a> 
```angelscript
[flake8]
max-line-length = 119
ignore = E203, W503
exclude = .git, __pycache__, venv, .venv, */migrations/*,
```

---

# <a id="title18">18. Описание файла mypy.ini</a> 
```ini
# Настроил mypy для Django, указав путь к settings.py.
# Это нужно было чтоб убрать ошибки проверки mypy
# из-за того, что он не распознавал phonenumber_field,
# так как у phonenumber_field нет type stubs.
[mypy]
plugins = mypy_django_plugin.main

# Указываем настройки для плагина Django.
[mypy.plugins.django-stubs]
django_settings_module = config.settings

# Пробовал игнорировать phonenumber_field в mypy.ini,
# но это не сработало, и поэтому пришлось добавить
# в код (users/models.py) вот это "# type: ignore"
# на импорт PhoneNumberField, и ошибка исчезла.
[mypy-phonenumber_field.*]
ignore_missing_imports = True
```

---

# <a id="title19">19. Описание файла .coveragerc</a> 
```ini
# Настройки для расчета покрытия кода так, чтоб считалось только по рабочим приложениям (например, habits, users, telegram_bot) 
# и игнорировало тесты, миграции, manage.py и прочее.
[run]
branch = True
source =
    habits
    users
    telegram_bot
omit =
    */migrations/*
    */tests.py
    manage.py
    config/*
    */__init__.py

[report]
show_missing = True
skip_covered = True
```

---

# <a id="title20">20. Документация к API</a> 
1. ***Swagger UI*** по адресу: http://127.0.0.1:8000/swagger/
2. ***Redoc*** по адресу: http://127.0.0.1:8000/redoc/

---

# <a id="title21">21. Установка проекта</a>
1. Клонируйте репозиторий:
   ```
   git clone https://github.com/MaksimLakovich/Habits-tracker.git
   ```
2. Установите зависимости:
   ```
   poetry install
   ```
3. Заполните файл `.env` по примеру `.env.example`

---

# <a id="title22">22. Установка и запуск проекта на сервере (через Docker и Nginx)</a>

1. Клонируйте репозиторий:
    ```commandline
    git clone https://github.com/MaksimLakovich/Habits-tracker.git
    cd Habits-tracker.git
    ```

2. Создайте файл окружения ***.env.docker*** (на основе примера *.env.docker.example*) и заполните его реальными данными:
    ```commandline
    cp .env.docker.example .env.docker
    nano .env.docker
    ```
   
3. Соберите и запустите контейнеры:
    ```commandline
    docker-compose up -d --build
    ```
   
4. Выполните миграции и соберите статику (если они ещё не применялись):
    ```commandline
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py collectstatic --noinput
    ```
   
5. После успешного запуска приложение будет доступно по IP-адресу вашей ВМ на порту 80: `http://<ваш-ip>`

---

# <a id="title23">23. Автоматический деплой через GitHub Actions</a> 

Репозиторий настроен на автоматический деплой через GitHub Actions.

1. При каждом push в ветку main происходит:
   - запуск линтера (flake8),
   - запуск тестов (с использованием SQLite),
   - сборка Docker-образа,
   - публикация образа в Docker Hub,
   - деплой на удалённый сервер (IP: 158.160.199.127:8081 - ***ДЛЯ ИНФО!* В проекте используется динамический IP-адрес поэтому может измениться со временем!**).
2. Для работы пайплайна настроены секреты в GitHub:
   - для публикации образов:
     - DOCKER_HUB_USERNAME
     - DOCKER_HUB_ACCESS_TOKEN
   - для деплоя на сервер:
     - SSH_USER
     - SERVER_IP
     - SSH_KEY

После успешного выполнения пайплайна приложение автоматически обновляется и доступно по адресу:

http://158.160.199.127:8081/admin/
