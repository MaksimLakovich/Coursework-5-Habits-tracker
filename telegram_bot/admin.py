from django.contrib import admin

from telegram_bot.models import TelegramProfile


@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "app_user", "telegram_chat_id", "telegram_user_id", "created_at", "updated_at",)
    list_filter = ("app_user", "telegram_chat_id",)
    search_fields = ("app_user__email", "telegram_chat_id", "telegram_user_id",)
    ordering = ("app_user",)
