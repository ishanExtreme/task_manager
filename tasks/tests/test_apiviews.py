from rest_framework.test import APITestCase
from ..models import Task
from django.contrib.auth.models import User


class TaskViewSetTest(APITestCase):
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
            title="Task with title 2", priority=2, user=self.user, deleted=True
        )
        self.task2.save()
        user2 = User(username="ishan", email="ishan@wayne.org", password="welcome@123")
        user2.save()
        self.task3 = Task(
            title="Task with title 3 and of user 2", priority=2, user=user2
        )
        self.task3.save()
        self.client.login(username="bruce_wayne", password="i_am_batman")

    def test_deletd_tasks_are_not_returned(self):
        response = self.client.get("/api/task/")
        self.assertEqual(len(response.data), 1)
        for task in response.data:
            self.assertEqual(task["title"], "Task with title 1")

    def test_create_properly_assigns_user(self):
        response = self.client.post(
            "/api/task/",
            {"title": "Temporary Task", "description": "random", "priority": 1},
        )
        self.assertEqual(response.data["user"]["username"], "bruce_wayne")

    def test_other_users_tasks_cannot_be_seen(self):
        response = self.client.get(f"/api/task/{self.task3.id}/")
        self.assertEqual(response.status_code, 404)

    def test_other_users_tasks_cannot_be_updated(self):
        response = self.client.put(
            f"/api/task/{self.task3.id}/",
            {"title": "Temporary Task", "description": "random", "priority": 1},
        )
        self.assertEqual(response.status_code, 404)

    def test_other_users_tasks_cannot_be_deleted(self):
        response = self.client.delete(f"/api/task/{self.task3.id}/")
        self.assertEqual(response.status_code, 404)
