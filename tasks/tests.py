from django.test import TestCase

# Create your tests here.


class TestTaskManager(TestCase):
    def test_a_add_task(self):
        """Test Adding Tasks"""
        task_name = "Test1"
        response = self.client.get("/add-task/", {"task": task_name})
        self.assertEqual(response.status_code, 302)

    def test_a_delete_task(self):
        """Test Deleting Tasks"""
        task_name = "Test2"
        self.client.get("/add-task/", {"task": task_name})
        response = self.client.get("/delete-task/1/")
        self.assertEqual(response.status_code, 302)

    def test_a_view_task(self):
        """Test Viewing Tasks"""
        task_name = "Luke Skywalker"
        self.client.get("/add-task/", {"task": task_name})
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(task_name, response.content.decode())

    def test_b_view_task(self):
        """Complete a given task and ensure its in the completed view"""
        task_name = "Darth Vader"
        self.client.get("/add-task/", {"task": task_name})
        response = self.client.get("/completed_tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(task_name, response.content.decode())
        t = self.client.get("/complete_task/3/")
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(task_name, response.content.decode())
        response = self.client.get("/completed_tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(task_name, response.content.decode())
