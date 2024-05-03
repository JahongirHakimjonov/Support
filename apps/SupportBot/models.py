from django.db import models
from apps.shared.models import AbstractBaseModel


class BotUsers(AbstractBaseModel):
    USER_ROLE = (
        ("admin", "Admin"),
        ('moderator', 'Moderator'),
        ("user", "User"),
    )
    LANGUAGE_CODE = (
        ("uz", "O'zbek"),
        ("ru", "Русский"),
        ("en", "English"),
    )

    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.BigIntegerField(max_length=100, null=True, blank=True)
    language_code = models.CharField(max_length=10, choices=LANGUAGE_CODE, default="uz")
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=10, choices=USER_ROLE, default="user")

    class Meta:
        verbose_name = "Bot User"
        verbose_name_plural = "Bot Foydalanuvchilari"
        db_table = "bot_users"

    def __str__(self):
        return self.first_name if self.first_name else "Bot User"


class TelegramGroupID(AbstractBaseModel):
    group_id = models.BigIntegerField(unique=True)
    group_name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Telegram Group ID"
        verbose_name_plural = "Telegram Group IDs"
        db_table = "telegram_group_id"

    def __str__(self):
        return self.group_name


class TelegramChannelID(AbstractBaseModel):
    channel_id = models.BigIntegerField(unique=True)
    channel_name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Telegram Channel ID"
        verbose_name_plural = "Telegram Channel IDs"
        db_table = "telegram_channel_id"

    def __str__(self):
        return self.channel_name


class DailyMessages(AbstractBaseModel):
    telegram_id = models.BigIntegerField()
    message_date = models.DateField()
    message_count = models.IntegerField()

    def __str__(self):
        return f"{self.telegram_id}"

    class Meta:
        verbose_name_plural = "Kunlik xabarlar"
        db_table = "daily_message"
