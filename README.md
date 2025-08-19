# HABITS TRACKER API (Django REST Framework)


[1. Цель проекта](#title1) / 
[2. Модели](#title2) / 
[3. Админки](#title3) / 
[4. Сериализации](#title4) / 
[5. Валидация](#title5) / 
[6. Контроллеры](#title6) / 
[7. Права доступов](#title7) / 
[8. Пагинация](#title8) / 
[9. Интеграция с платежной системой (сервисные функции)](#title9) / 
[10. Вспомогательные функции](#title10) / 
[11. Сигналы](#title11) / 
[12. Отложенные задачи](#title12) / 
[13. Загрузка тестовых данных](#title13) / 
[14. Тестирование приложения](#title14) /
[15. Установка проекта](#title15) / 
[16. Получение ключей .env](#title16) / 
[17. Описание файла .flake8](#title17) / 
[18. Описание файла mypy.ini](#title18) / 
[19. Документация к API](#title19) / 




# <a id="title1">1. Цель проекта</a>
Backend-часть SPA веб-приложения (трекер полезных привычек), которое посвящено приобретению новых полезных привычек и искоренению старых плохих привычек.
Разработка выполнена над SPA веб-приложением и результатом создания проекта будет бэкенд-сервер, который возвращает клиенту JSON-структуры.




# <a id="title2">2. Описание моделей (models)</a>

## _Приложение "Users" (users/models.py):_

1) Модель данных `?` - представляет Пользователя ...

## _Приложение "Habits" (habits/models.py):_

1) Модель данных `` - представляет ...




# <a id="title3">3. Описание админок (admin)</a>

## _Приложение "Users" (users/admin.py):_

1) Админка `` - отображение данный модели ...

## _Приложение "Habits" (habits/admin.py):_

1) Админка `` - отображение данный модели ...




# <a id="title4">4. Описание сериализаций (serializers)</a>

## _Приложение "Users" (users/serializers.py):_

1) Сериализатор `` - ...

## _Приложение "Habits" (habits/serializers.py):_

1) Сериализатор `` - ...




# <a id="title5">5. Описание валидации (validators)</a>

## _Приложение ""Habits" (habits/validators.py):_

1) Класс-валидатор `` - ...




# <a id="title6">6. Описание контроллеров (views)</a>

## _Приложение "Users" (users/views.py):_

1) Класс-контроллер `` - ...

## _Приложение "Habits" (habits/views.py):_

1) Класс-контроллер `` - ...




# <a id="title7">7. Описание прав доступов (permissions)</a>

## _Приложение "Users" (users/permissions.py):_

1) Класс `` - кастомный permission-класс...




# <a id="title8">8. Описание пагинации (paginators)</a>

## _Приложение "Habits" (habits/paginators.py):_

1) Класс `` - общий пагинатор для ...




# <a id="title9">9. Интеграция. Описание сервисных функций (services)</a>

## _Приложение "Users" (users/services.py):_

1) ...

## _Приложение "Habits" (habits/services.py):_

1) ...




# <a id="title10">10. Вспомогательные функции</a>

## _Приложение "Users" (users/managers.py):_

1) ...




# <a id="title11">11. Сигналы</a>

## _Приложение "Habits" (habits/signals.py):_

1) Сигнал `` - для ...




# <a id="title12">12. Отложенные задачи</a>

## _Приложение "Users" (users/tasks.py):_

1) Периодическая задача `` - ...

## _Приложение "Habits" (habits/tasks.py):_

1) Отложенная задача `` - ...




# <a id="title13">13. Загрузка тестовых данных</a>

## _Директория проекта для различных данных (data/fixtures):_
1. Файл `.json` - фикстура с тестовыми данными для ...
2. Файл `groups.json` - фикстура с данными группы "Moderators" и добавления в нее набора прав доступов.

## _Приложение "Habits" (habits/management/commands):_
1. `add_habits.py` - код кастомной команды по загрузке данных из `habits.json`.

## _Приложение "Users" (users/management/commands):_
1. `add_users.py` - код кастомной команды по cозданию тестовых пользователей через create_user().




# <a id="title14">14. Тестирование приложения</a>

## _Приложение "Habits" (habits/tests.py):_

1) Команды для проверки покрытия тестами:
   ```
   coverage run manage.py test
   coverage report
   coverage html
   ```

2) Класс `` - тесты, которые будут проверять корректность работы CRUD для ...:
   - `test_...` - тест ...




# <a id="title15">15. Установка проекта</a>
1. Клонируйте репозиторий:
   ```
   git clone https://github.com/MaksimLakovich/Coursework-5-Habits-tracker.git
   ```
2. Установите зависимости:
   ```
   poetry install
   ```
3. Заполните файл `.env` по примеру `.env.example`




# <a id="title16">16. Получение ключей. Описание файла .env.example</a> 
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




# <a id="title17">17. Описание файла .flake8</a> 
```angelscript
[flake8]
max-line-length = 119
ignore = E203, W503
exclude = .git, __pycache__, venv, .venv
```




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




# <a id="title19">19. Документация к API</a> 
1. ***Swagger UI*** по адресу: http://127.0.0.1:8000/swagger/
2. ***Redoc*** по адресу: http://127.0.0.1:8000/redoc/
