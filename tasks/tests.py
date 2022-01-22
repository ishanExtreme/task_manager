from django.test import TestCase

from tasks.models import Task

# Create your tests here.


class TestTaskManager(TestCase):
    def test_add_task(self):
        """Test Adding Tasks"""
        task_name = "Test1"
        response = self.client.get("/add-task/", {"task": task_name})
        self.assertEqual(response.status_code, 302)

    def test_delete_task(self):
        """Test Deleting Tasks"""
        task_name = "Test2"
        self.client.get("/add-task/", {"task": task_name})
        task_object = Task.objects.filter(title=task_name).first()
        self.assertIsNotNone(task_object)
        response = self.client.get(f"/delete-task/{task_object.id}/")
        self.assertEqual(response.status_code, 302)

    def test_a_view_task(self):
        """Test Viewing Tasks"""
        task_name = "learn to use the force"
        self.client.get("/add-task/", {"task": task_name})
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(task_name, response.content.decode())

    def test_b_view_task(self):
        """Complete a given task and ensure its in the completed view"""
        task_name = "learn the ways of the force"
        self.client.get("/add-task/", {"task": task_name})
        response = self.client.get("/completed_tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(task_name, response.content.decode())
        task_object = Task.objects.filter(title=task_name).first()
        self.assertIsNotNone(task_object)
        t = self.client.get(f"/complete_task/{task_object.id}/")
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(task_name, response.content.decode())
        response = self.client.get("/completed_tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(task_name, response.content.decode())
