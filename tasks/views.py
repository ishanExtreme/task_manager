from re import template
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView


class UserCreationView(CreateView):
    form_class = UserCreationForm
    template_name = "form_template.html"
    success_url = "/user/login"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["f_heading"] = "Sign Up"
        return context


class UserLoginView(LoginView):
    template_name = "form_template.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["f_heading"] = "Login"
        return context
