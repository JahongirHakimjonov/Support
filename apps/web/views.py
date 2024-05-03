from django.views.generic import TemplateView

from apps.web.models import Home


class HomePageView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["home"] = Home.objects.first()
        return context
