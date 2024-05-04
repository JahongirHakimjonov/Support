from django.contrib import admin
from apps.web.models import Home, About, SiteUsers


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "description", "address", "phone", "email")
    search_fields = ("name",)


@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ("full_name", "date", "age", "info")
    search_fields = ("full_name",)


@admin.register(SiteUsers)
class SiteUsersAdmin(admin.ModelAdmin):
    list_display = ("useremail",)
    search_fields = ("useremail",)
