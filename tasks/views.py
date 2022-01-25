from django.http import HttpResponseRedirect
from tasks.models import Task
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm, ValidationError


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
        return Task.objects.filter(deleted=False, user=self.request.user)


class TaskListView(LoginRequiredMixin, ListView):
    template_name = "tasks.html"
    # name in html file(dict)
    context_object_name = "tasks"

    def get_queryset(self):
        filter = self.request.GET.get("filter")
        tasks = Task.objects.filter(deleted=False, user=self.request.user).order_by(
            "priority"
        )
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


class TaskCreateForm(ModelForm):
    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 10:
            raise ValidationError("Data too small")
        return title.upper()

    def clean_priority(self):
        # Set the right priority
        priority = self.cleaned_data["priority"]
        inc_priority = priority
        curr_id = None
        while True:
            found = False
            if (
                Task.objects.filter(deleted=False, priority=inc_priority)
                .exclude(id=curr_id)
                .exists()
            ):

                task = Task.objects.exclude(id=curr_id).get(
                    deleted=False, priority=inc_priority
                )
                task.priority = inc_priority + 1
                task.save()

                inc_priority += 1
                curr_id = task.id
                found = True
            if not found:
                break
        return priority

    class Meta:
        model = Task
        fields = ["title", "description", "completed", "priority"]


class AddTaskView(CreateView):
    form_class = TaskCreateForm
    template_name = "task_form.html"
    success_url = "/tasks"

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


class TaskDeleteView(AuthorizedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"


# class DisplayTaksView()
