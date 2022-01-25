from tasks.models import Task
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


class UserCreationView(CreateView):
    form_class = UserCreationForm
    template_name = "form_template.html"
    success_url = "/user/login"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add heading
        context["f_heading"] = "Sign Up"
        return context


class UserLoginView(LoginView):
    template_name = "form_template.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add heading
        context["f_heading"] = "Login"
        return context


class AuthorizedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(delete=False, user=self.request.user)


class TaskListView(LoginRequiredMixin, ListView):
    template_name = "tasks.html"
    # name in html file(dict)
    context_object_name = "tasks"

    def get_queryset(self):
        filter = self.request.GET.get("filter")
        tasks = Task.objects.filter(deleted=False, user=self.request.user)
        if filter:
            if filter == "pending":
                tasks = tasks.filter(completed=False)
            else:
                tasks = tasks.filter(completed=True)

        return tasks

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # count complete and incomplete tasks
        complete_count = Task.objects.filter(
            deleted=False, user=self.request.user, completed=True
        ).count()
        total_count = Task.objects.filter(deleted=False, user=self.request.user).count()
        context["complete_count"] = complete_count
        context["total_count"] = total_count

        # add filter to the dict
        filter = self.request.GET.get("filter")
        if filter:
            context["filter"] = filter
        return context


# class DisplayTaksView()
