from django.contrib import admin
from apps.web.models import Home


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "description", "address", "phone", "email")
    search_fields = ("name",)
