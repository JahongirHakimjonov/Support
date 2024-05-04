from django.views.generic import TemplateView, FormView
from django.contrib import messages

from apps.web.forms import UserCreateForm
from apps.web.models import Home, About, SiteUsers


class HomePageView(FormView):
    template_name = "index.html"
    form_class = UserCreateForm
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["home"] = Home.objects.first()
        return context

    def form_valid(self, form):
        useremail = form.cleaned_data.get("useremail")

        SiteUsers.objects.create(
            useremail=useremail
        )
        messages.success(
            self.request,
            "Ro'yxatdan o'tdingiz, tez orada siz bilan bog'lanishadi. Rahmat!",
        )
        return super().form_valid(form)


def homepage(request):
    home = Home.objects.first()
    return {"home": home}


def about(request):
    about = About.objects.first()
    return {"about": about}
