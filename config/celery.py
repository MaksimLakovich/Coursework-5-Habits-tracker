from __future__ import absolute_import, unicode_literals

import os

from celery import Celery  # type: ignore

# Установка переменной окружения для настроек проекта. Указывает Celery, где искать настройки Django.
# Без этого Celery не будет знать, какой проект загружать (вместо 'my_project' нужно указать 'config'):
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Создание экземпляра объекта Celery
# 'config' здесь — это просто имя (идентификатор), не обязательно совпадать с названием проекта.
app = Celery("config")

# Загрузка настроек из файла Django. Загружает все настройки, начинающиеся с CELERY_ из settings.py.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение и регистрация задач из файлов tasks.py в приложениях Django.
# Celery будет автоматически искать файлы tasks.py в каждом приложении Django. Это значит,
# что не нужно вручную регистрировать каждую задачу.
app.autodiscover_tasks()
