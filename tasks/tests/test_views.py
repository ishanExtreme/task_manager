from datetime import time
from django.test import TestCase
from django.test import RequestFactory
from ..views import (
    TaskListView,
    TaskCreateForm,
    AddTaskView,
)
from django.contrib.auth.models import User
from ..models import Schedule, Task


class UserCreationViewTest(TestCase):
    def test_user_created(self):
        response = self.client.post(
            "/user/signup/",
            {
                "username": "ishan",
                "password1": "welcome@123",
                "password2": "welcome@123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login")

    def test_get_context_data(self):
        response = self.client.get("/user/signup/")
        self.assertEqual(response.context["f_heading"], "Sign Up")


class UserLoginViewTest(TestCase):
    def setUp(self):
        user = User(username="ishan", email="bruce@wayne.org")
        user.set_password("welcome@123")
        user.save()

    def test_user_logged_in(self):
        response = self.client.post(
            "/user/login/",
            {
                "username": "ishan",
                "password": "welcome@123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/tasks")

    def test_get_context_data(self):
        response = self.client.get("/user/login/")
        self.assertEqual(response.context["f_heading"], "Login")


class TaskListViewTest(TestCase):
    def setUp(self):
        self.user = User(
            username="bruce_wayne",
            email="bruce@wayne.org",
        )
        self.user.save()
        self.user.set_password("i_am_batman")
        self.user.save()
        self.task1 = Task(title="Task with title 1", priority=1, user=self.user)
        self.task1.save()
        self.task2 = Task(
            title="Task with title 2", priority=2, user=self.user, completed=True
        )
        self.task2.save()
        self.task3 = Task(
            title="Task with title 3", priority=3, user=self.user, deleted=True
        )
        self.task3.save()
        user2 = User(username="ishan", email="ishan@wayne.org", password="welcome@123")
        user2.save()
        task4 = Task(title="Task with title 4 and of user 2", priority=2, user=user2)
        task4.save()

    def test_if_not_authenticated_redirects(self):
        """
        It should redirect to login page for anonymous user
        """
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/tasks/")

    def test_if_authenticated(self):
        """
        It should display the tasks page if user is authenticated
        """
        request = RequestFactory().get("/tasks/")
        request.user = self.user
        response = TaskListView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_only_current_users_task_are_returned(self):
        """
        Only current logged in user tasks should be returned
        """
        # login current user
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.get("/tasks/")
        # contains current user has 2 undeleted task
        self.assertEqual(len(response.context["tasks"]), 2)
        for task in response.context["tasks"]:
            # all tasks belong to current user
            self.assertEqual(task.user.id, self.user.id)

    def test_all_filter(self):
        """
        if nothing is supplied in url it should display all tasks(non deleted)
        """
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.get("/tasks/")
        # contains both completed and incompleted task
        self.assertEqual(len(response.context["tasks"]), 2)
        for task in response.context["tasks"]:
            # all tasks are non deleted in format
            self.assertEqual(task.deleted, False)

    def test_pending_filter(self):
        """
        if pending is supplied in url it should display only pending tasks
        """
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.get("/tasks/?filter=pending")
        # contains both completed and incompleted task
        self.assertEqual(len(response.context["tasks"]), 1)
        for task in response.context["tasks"]:
            # all tasks are non deleted in format
            self.assertEqual(task.deleted, False)
            self.assertEqual(task.completed, False)

    def test_completed_filter(self):
        """
        if completed is supplied in url it should display only completed tasks
        """
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.get("/tasks/?filter=completed")
        # contains both completed and incompleted task
        self.assertEqual(len(response.context["tasks"]), 1)
        for task in response.context["tasks"]:
            # all tasks are non deleted in format
            self.assertEqual(task.deleted, False)
            self.assertEqual(task.completed, True)

    def test_task_count_context(self):
        """
        It should correctly record count of completed and all tasks
        """
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.get("/tasks/")
        self.assertEqual(response.context["complete_count"], 1)
        self.assertEqual(response.context["total_count"], 2)


class TaskCreateFormTest(TestCase):
    def test_title_smaller_than_10_char(self):
        """
        Should return error if title is smaller than 10 character
        """
        form = TaskCreateForm(data={"title": "Title-1", "priority": 1})
        self.assertEqual(form.errors["title"], ["Data too small"])


class AddTaskViewTest(TestCase):
    def setUp(self):
        self.user = User(
            username="bruce_wayne",
            email="bruce@wayne.org",
        )
        self.user.save()
        self.user.set_password("i_am_batman")
        self.user.save()

    def test_if_not_authenticated_redirects(self):
        """
        It should redirect to login page for anonymous user
        """
        response = self.client.get("/create-task/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/create-task/")

    def test_if_authenticated(self):
        """
        It should display the create tasks page if user is authenticated
        """
        request = RequestFactory().get("/create-task/")
        request.user = self.user
        response = AddTaskView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_task_title_is_capitalized(self):
        """
        task title should be capitalized
        this also tests that user is assigned properly
        """
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.post(
            "/create-task/",
            {"title": "title in small case", "description": "random", "priority": 1},
        )
        task = Task.objects.filter(user=self.user).first()
        self.assertEqual(task.title, "TITLE IN SMALL CASE")

    def test_get_context_data(self):
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.get("/create-task/")
        self.assertEqual(response.context["f_heading"], "Add Task")


class UpdateTaskViewTest(TestCase):
    def setUp(self):
        self.user = User(
            username="bruce_wayne",
            email="bruce@wayne.org",
        )
        self.user.save()
        self.user.set_password("i_am_batman")
        self.user.save()
        user2 = User(username="ishan", email="ishan@wayne.org", password="welcome@123")
        user2.save()
        self.task1 = Task(title="Task with title 1", priority=1, user=self.user)
        self.task1.save()
        self.task2 = Task(title="Task with title 2", priority=1, user=user2)
        self.task2.save()

    def test_if_not_authenticated_redirects(self):
        """
        It should redirect to login page for anonymous user
        """
        response = self.client.get(f"/update-task/{self.task1.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f"/user/login?next=/update-task/{self.task1.id}/"
        )

    def test_if_not_authorized(self):
        """
        It should give 404 if user tries to access other user's task
        """
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.get(f"/update-task/{self.task2.id}/")
        self.assertEqual(response.status_code, 404)

    def test_updation(self):
        """
        task should be updated
        """
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.post(
            f"/update-task/{self.task1.id}/",
            {"title": "new task title", "description": "random", "priority": 1},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/tasks/")
        updated_task = Task.objects.get(id=self.task1.id)
        self.assertEqual(updated_task.title, "NEW TASK TITLE")

    def test_get_context_data(self):
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.get(f"/update-task/{self.task1.id}/")
        self.assertEqual(response.context["f_heading"], "Update Task")


class TaskDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User(
            username="bruce_wayne",
            email="bruce@wayne.org",
        )
        self.user.save()
        self.user.set_password("i_am_batman")
        self.user.save()
        user2 = User(username="ishan", email="ishan@wayne.org", password="welcome@123")
        user2.save()
        self.task1 = Task(title="Task with title 1", priority=1, user=self.user)
        self.task1.save()
        self.task2 = Task(title="Task with title 2", priority=1, user=user2)
        self.task2.save()

    def test_if_not_authenticated_redirects(self):
        """
        It should redirect to login page for anonymous user
        """
        response = self.client.get(f"/delete-task/{self.task1.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f"/user/login?next=/delete-task/{self.task1.id}/"
        )

    def test_if_not_authorized(self):
        """
        It should give 404 if user tries to access other user's task
        """
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.get(f"/delete-task/{self.task2.id}/")
        self.assertEqual(response.status_code, 404)

    def test_deletion(self):
        """
        task should be deleted
        """
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.post(
            f"/delete-task/{self.task1.id}/",
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/tasks/")
        tasks = Task.objects.filter(user=self.user)
        self.assertEqual(tasks.count(), 0)


class ScheduleRequestTest(TestCase):
    def setUp(self):
        self.user = User(
            username="bruce_wayne",
            email="bruce@wayne.org",
        )
        self.user.save()
        self.user.set_password("i_am_batman")
        self.user.save()

        user2 = User(username="ishan", email="ishan@wayne.org", password="welcome@123")
        user2.save()
        self.schedule_2 = Schedule(user=user2)
        self.schedule_2.save()

    def test_if_not_authenticated_redirects(self):
        """
        It should redirect to login page for anonymous user
        """
        response = self.client.get("/report/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/report/")

    def test_if_user_dont_have_schedule(self):
        """
        it should redirect request to AddScheduleView
        """
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.post("/report/", {"time": "00:00:00"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/tasks/")
        schedule = self.user.schedule
        self.assertEquals(schedule.time, time(0, 0))

    def test_update_user_schedule(self):
        """
        If user already have a schedule then UpdateScheduleView should be called and
        schedule should be updated properly
        """
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.post("/report/", {"time": "12:02:00"})
        # Create schedule for user
        self.client.post("/report/", {"time": "00:00:00"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/tasks/")
        schedule = self.user.schedule
        self.assertEquals(schedule.time, time(12, 2))

    def test_schedule_manager_if_not_authenticated(self):
        response = self.client.get(f"/update-schedule/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/user/login?next=/update-schedule/1/")

    def test_schedule_manager_if_not_authorized(self):
        self.client.login(username="bruce_wayne", password="i_am_batman")
        response = self.client.get(f"/update-schedule/{self.schedule_2.id}/")
        self.assertEqual(response.status_code, 404)

    def test_schedule_manager_context_data(self):
        self.client.login(username="bruce_wayne", password="i_am_batman")
        # Create schedule for user
        self.client.post("/report/", {"time": "00:00:00"})
        response = self.client.get(f"/update-schedule/{self.user.schedule.id}/")
        self.assertEqual(response.context["f_heading"], "Schedule Report")
