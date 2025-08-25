# HABITS TRACKER API (Django REST Framework)


[1. Цель проекта](#title1) / 
[2. Модели](#title2) / 
[3. Админки](#title3) / 
[4. Сериализация](#title4) / 
[5. Валидация](#title5) / 
[6. Контроллеры](#title6) / 
[7. Маршруты](#title7) / 
[8. Права доступов](#title8) / 
[9. Пагинация](#title9) / 
[10. Интеграция с платежной системой (сервисные функции)](#title10) / 
[11. Вспомогательные функции](#title11) / 
[12. Сигналы](#title12) / 
[13. Отложенные задачи](#title13) / 
[14. Загрузка тестовых данных](#title14) / 
[15. Тестирование приложения](#title15) /
[16. Установка проекта](#title16) / 
[17. Получение ключей .env](#title17) / 
[18. Описание файла .flake8](#title18) / 
[19. Описание файла mypy.ini](#title19) / 
[20. Документация к API](#title20) / 




# <a id="title1">1. Цель проекта</a>
Backend-часть SPA веб-приложения (трекер полезных привычек), которое посвящено работе по приобретению новых полезных привычек и искоренению старых плохих привычек.
Разработка выполнена над SPA веб-приложением и результатом проекта является бэкенд-сервер, который возвращает клиенту JSON-структуры.




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




# <a id="title3">3. Описание админок (admin)</a>

## _Приложение "Users" (users/admin.py):_

1) Админка `AppUserAdmin(UserAdmin)` - отображение данных модели *AppUser* (Пользователь) в админке.

## _Приложение "Habits" (habits/admin.py):_

1) Админка `HabitsAdmin(admin.ModelAdmin)` - отображение данных модели *Habits* (Привычка) в админке.




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
     - Подключенные сторонние кастомные валидаторы:
       - `HabitRewardChoiceValidator()`




# <a id="title5">5. Описание валидации (validators)</a>

## _Приложение ""Habits" (habits/validators.py):_

1) Класс-валидатор `HabitRewardChoiceValidator()` - для проверки:
   - нельзя одновременно указать связанную привычки и вознаграждение;
   - должно быть указано хотя бы одно из двух полей.




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
     - `perform_create(self, serializer)`: присваивает текущего авторизованного пользователя как владельца (owner) создаваемого объекта.

2) Класс-контроллер `UserHabitsListAPIView(generics.ListAPIView)` - для получения списка привычек текущего пользователя:
   - на основе ***generics***.
   - методы:
     - `get_queryset(self)`: получение набора данных, который будет использоваться во View.

3) Класс-контроллер `PublicHabitsListAPIView(generics.ListAPIView)` - для получения списка публичных привычек:
   - на основе ***generics***.
   - методы:
     - `get_queryset(self)`: получение набора данных, который будет использоваться во View.

4) Класс-контроллер `HabitsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView)` - для просмотра, обновления и удаления конкретной привычки:
   - на основе ***generics***.
   - валидация:
     - `permission_classes = [IsOwner]`: пользователь имеет доступ только к своим привычкам по механизму CRUD




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




# <a id="title8">8. Описание прав доступов (permissions)</a>

## _Приложение "Users" (users/permissions.py):_

1) Класс `IsSelf(BasePermission)` - кастомный permission-класс, который разрешает доступ только владельцу своего профиля.

## _Приложение "Habits" (habits/permissions.py):_

1) Класс `IsOwner(BasePermission)` - кастомный permission-класс, который проверяет, является ли пользователь владельцем (owner) объекта.




# <a id="title9">9. Описание пагинации (paginators)</a>

## _Приложение "Habits" (habits/paginators.py):_

1) Класс `` - общий пагинатор для ...




# <a id="title10">10. Интеграция. Описание сервисных функций (services)</a>

## _Приложение "Users" (users/services.py):_

1) ...

## _Приложение "Habits" (habits/services.py):_

1) ...




# <a id="title11">11. Вспомогательные функции</a>

## _Приложение "Users" (users/managers.py):_

1) Класс `AppUserManager(BaseUserManager)` - кастомный менеджер для пользователя без поля username:
   - функция `create_user()` - создает и возвращает обычного пользователя.
   - функция `create_superuser()` - создает и возвращает суперпользователя.




# <a id="title12">12. Сигналы</a>

## _Приложение "Habits" (habits/signals.py):_

1) Сигнал `` - для ...




# <a id="title13">13. Отложенные задачи</a>

## _Приложение "Users" (users/tasks.py):_

1) Периодическая задача `` - ...

## _Приложение "Habits" (habits/tasks.py):_

1) Отложенная задача `` - ...




# <a id="title14">14. Загрузка тестовых данных</a>

## _Директория проекта для различных данных (data/fixtures):_
1. Файл `.json` - фикстура с тестовыми данными для ...
2. Файл `groups.json` - фикстура с данными группы "Moderators" и добавления в нее набора прав доступов.

## _Приложение "Habits" (habits/management/commands):_
1. `add_habits.py` - код кастомной команды по загрузке данных из `habits.json`.

## _Приложение "Users" (users/management/commands):_
1. `add_users.py` - код кастомной команды по cозданию тестовых пользователей через create_user().




# <a id="title15">15. Тестирование приложения</a>

## _Приложение "Habits" (habits/tests.py):_

1) Команды для проверки покрытия тестами:
   ```
   coverage run manage.py test
   coverage report
   coverage html
   ```

2) Класс `` - тесты, которые будут проверять корректность работы CRUD для ...:
   - `test_...` - тест ...




# <a id="title16">16. Установка проекта</a>
1. Клонируйте репозиторий:
   ```
   git clone https://github.com/MaksimLakovich/Coursework-5-Habits-tracker.git
   ```
2. Установите зависимости:
   ```
   poetry install
   ```
3. Заполните файл `.env` по примеру `.env.example`




# <a id="title17">17. Получение ключей. Описание файла .env.example</a> 
1. Создайте файл .env в корне проекта из копии подготовленного файла `.env.example`, в котором описаны названия всех переменных, необходимых для работы приложения.
2. Замените значения переменных реальными данными.
3. В модуле `settings.py` существует секретный ключ `SECRET_KEY`, который рекомендуется в целях безопасности хранить в тайне:
4. Файл .env должен содержать данные:
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
```




# <a id="title18">18. Описание файла .flake8</a> 
```angelscript
[flake8]
max-line-length = 119
ignore = E203, W503
exclude = .git, __pycache__, venv, .venv
```




# <a id="title19">19. Описание файла mypy.ini</a> 
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




# <a id="title20">20. Документация к API</a> 
1. ***Swagger UI*** по адресу: http://127.0.0.1:8000/swagger/
2. ***Redoc*** по адресу: http://127.0.0.1:8000/redoc/
