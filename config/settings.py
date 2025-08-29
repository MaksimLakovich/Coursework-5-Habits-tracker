import os
from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv

# Загрузка переменных из .env-файла
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY_FOR_PROJECT')

DEBUG = True if os.getenv('DEBUG') == 'True' else False

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # обязательно, иначе UI не поднимется

    # Добавляем это чтобы библиотека https://django-phonenumber-field.readthedocs.io/en/stable/index.html
    # использовала локализованные ошибки валидации номеров в поле PhoneNumberField
    'phonenumber_field',

    # DRF (Django REST framework) - это библиотека, которая работает со стандартными моделями Django для создания
    # гибкого и мощного API-сервера для проекта.
    'rest_framework',

    # Добавление пакета celery-beat
    'django_celery_beat',

    # Добавление drf-yasg (Yet another Swagger generator for Django REST Framework) для API документации
    'drf_yasg',

    # CORS
    'corsheaders',

    # Приложения проекта
    'users',
    'habits',
    'telegram_bot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # должно быть выше CommonMiddleware
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT', default='5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.AppUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=180),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# Настройки для Celery
# URL-адрес брокера сообщений. Например, Redis, который по умолчанию работает на порту 6379 — адрес брокера сообщений.
# Формат: redis://<host>:<port>/<db_number>.
# /0 и /1 и так далее — разные базы в Redis (например, чтобы задачи Celery и кэш Django не мешали друг другу).
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
# URL-адрес брокера результатов — хранилище результатов выполнения задач. Можно использовать тот же Redis,
# что и для брокера.
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
# Часовой пояс для работы Celery — важно для периодических задач, чтобы они выполнялись в правильное время.
# Пример, CELERY_TIMEZONE = "Australia/Tasmania", я ссылаюсь на наш TIME_ZONE проекта, чтоб все было в одном поясе
CELERY_TIMEZONE = TIME_ZONE
# Флаг отслеживания выполнения задач — Celery будет отслеживать состояние "в процессе".
CELERY_TASK_TRACK_STARTED = True
# Максимальное время на выполнение задачи
CELERY_TASK_TIME_LIMIT = 30 * 60

# Настройки для Telegram-бота (отправка напоминаний)
TELEGRAM_API_URL = 'https://api.telegram.org/bot'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Настройка расписания запуска периодической задачи через Celery-beat
CELERY_BEAT_SCHEDULE = {
    'task-send-daily-message': {
        'task': 'telegram_bot.tasks.task_send_daily_message',
        'schedule': crontab(hour=9, minute=00),  # каждый день в 9:00
    },
}

# Настройки для CORS и CSRF
# Разрешаем только конкретные origin’ы (более безопасно)
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # это типичный адрес фронтенда во время разработки. Чтобы фронт мог в разработке
    # стучаться в наш Django API, нужно разрешить CORS с этого адреса. Если у нас нет фронтенда или он пока
    # не разрабатывается, то http://localhost:3000 - это просто заготовка для будущих разработчиков.
    'https://habits-frontend.example.com',  # продакшн фронтенд
]

# Для работы CSRF с кросс-доменными запросами (POST, PUT, DELETE)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'https://habits-frontend.example.com',
]

# Запрещаем доступ для всех подряд (оставляем только из списка выше)
CORS_ALLOW_ALL_ORIGINS = False

