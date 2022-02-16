from django.http import HttpResponseRedirect
from django.shortcuts import render
from tasks.models import Task, Schedule
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm, ValidationError, TimeInput
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User


def home_view(request):
    return render(request, "home.html")


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
        # count complete and incomplete tasks(UPDATED)
        # -------- Non-effiecient WAY REQUIRES QUERYING TWO TIME OVER WHOLE DATABASE --------
        # complete_count = Task.objects.filter(
        #     deleted=False, user=self.request.user, completed=True
        # ).count()
        # total_count = Task.objects.filter(deleted=False, user=self.request.user).count()
        # -------- Efficiend WAY -------------
        base_qs = Task.objects.filter(deleted=False, user=self.request.user)
        complete_count = base_qs.filter(completed=True).count()
        total_count = base_qs.count()
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

    class Meta:
        model = Task
        fields = ["title", "description", "completed", "priority"]


class AddTaskView(LoginRequiredMixin, CreateView):
    form_class = TaskCreateForm
    template_name = "task_form.html"
    success_url = "/tasks/"

    def form_valid(self, form):
        # get form model
        self.object = form.save(commit=False)
        # save currect user into user field
        self.object.user = self.request.user
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add heading
        context["f_heading"] = "Add Task"
        return context


class UpdateTaskView(AuthorizedTaskManager, UpdateView):
    form_class = TaskCreateForm
    template_name = "task_form.html"
    success_url = "/tasks/"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add heading
        context["f_heading"] = "Update Task"
        return context


class TaskDeleteView(AuthorizedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks/"


# This will handle the schedule update request if schedule doesnot exists
# it will create it for user and if it exists it will redirect user to that schedule
@login_required
def handle_schedule_request(request):

    user_schedule = Schedule.objects.filter(user=request.user)
    if user_schedule.exists():
        user_schedule = user_schedule.first()
        return HttpResponseRedirect(f"/update-schedule/{user_schedule.id}")
    else:
        return AddScheduleView.as_view()(request)


# Schedule generic form
class ScheduleForm(ModelForm):
    class Meta:
        model = Schedule
        fields = ["time"]
        # Change type from text to time
        # Wrong render of time in update view if using widget
        # widgets = {"time": TimeInput(attrs={"type": "time"})}


class SheduleManager(LoginRequiredMixin):

    # In case anyone calls the url manually check if they are editing there own
    # schedule
    def get_queryset(self):
        return Schedule.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add heading
        context["f_heading"] = "Schedule Report"
        return context


class AddScheduleView(SheduleManager, CreateView):
    form_class = ScheduleForm
    success_url = "/tasks/"
    template_name = "form_template.html"

    def form_valid(self, form):
        # get form model
        self.object = form.save(commit=False)
        # save currect user into user field
        self.object.user = self.request.user
        # reset prev_sent_time
        self.object.prev_sent_time = None
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


# TODO: Restrict user to update schedule to next 5-10 minutes
class UpdateScheduleView(SheduleManager, UpdateView):
    form_class = ScheduleForm
    success_url = "/tasks/"
    template_name = "form_template.html"

    def form_valid(self, form):
        # get form model
        self.object = form.save(commit=False)
        # reset prev_sent_time
        self.object.prev_sent_time = None
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


# class DisplayTaksView()
