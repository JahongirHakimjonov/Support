from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username="Jahongir").exists():
            User.objects.create_superuser(
                "Jahongir", "jahongirhakimjonov@gmail.com", "1253"
            )
