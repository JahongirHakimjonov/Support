from django.urls import path

from apps.web.views import HomePageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
]
