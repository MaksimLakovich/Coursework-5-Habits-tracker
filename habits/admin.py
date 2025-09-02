from django.contrib import admin

from habits.models import Habits


@admin.register(Habits)
class HabitsAdmin(admin.ModelAdmin):
    """Настройка отображения данных модели *Habits* (Привычка) в админке."""

    list_display = (
        "id",
        "owner",
        "location",
        "time",
        "description",
        "is_pleasant",
        "is_public",
        "related_pleasant_habit",
        "reward",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "owner",
        "location",
        "time",
        "is_pleasant",
        "is_public",
    )
    search_fields = (
        "owner__email",
        "location",
        "time",
        "description",
    )
    ordering = ("owner", "description",)
