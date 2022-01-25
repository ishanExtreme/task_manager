from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView


class UserCreationView(CreateView):
    form_class = UserCreationForm
    template_name = "user_create.html"
    success_url = "/user/login"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["f_heading"] = "Sign Up"
        return context
