from rest_framework.pagination import PageNumberPagination


class BaseHabitsListPagination(PageNumberPagination):
    """Чтобы не дублировать код, создал базовый класс и от него наследуюсь в страницах со списками."""
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 50


class UserHabitsListPagination(BaseHabitsListPagination):
    """Вывод по 5 привычек на странице /habits/user/."""
    pass


class PublicHabitsListPagination(BaseHabitsListPagination):
    """Вывод по 10 привычек на странице /habits/public/."""
    page_size = 10
