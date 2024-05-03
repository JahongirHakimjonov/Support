from django.contrib import admin

from apps.SupportBot.models import BotUsers, DailyMessages, TelegramChannelID, TelegramGroupID


@admin.register(BotUsers)
class BotUsersAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "username", "phone", "role", "is_active")
    search_fields = ("first_name", "last_name", "username", "phone")
    list_filter = ("role", "is_active")


@admin.register(TelegramGroupID)
class TelegramGroupIDAdmin(admin.ModelAdmin):
    list_display = ("group_id", "group_name")
    search_fields = ("group_id", "group_name")
    list_per_page = 10


@admin.register(TelegramChannelID)
class TelegramChannelIDAdmin(admin.ModelAdmin):
    list_display = ("channel_id", "channel_name")
    search_fields = ("channel_id", "channel_name")
    list_per_page = 10


@admin.register(DailyMessages)
class DailyMessagesAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "message_date", "message_count")
    search_fields = ("telegram_id", "message_date")
    list_per_page = 10
