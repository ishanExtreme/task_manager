from django.test import TestCase
from ..models import Schedule, Task, History
from django.contrib.auth.models import User


class TaskTest(TestCase):
    def setUp(self):
        self.user = User(
            username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman"
        )
        self.user.save()
        self.task = Task(title="Task with priority 1", priority=1, user=self.user)
        self.task.save()

    def test_str(self):
        """
        It should outputs the title of task
        """
        self.assertEqual(str(self.task), "Task with priority 1")

    def test_set_prev_state_and_get_prev_state(self):
        """
        value returned from getter methid should be equal to the value passed in
        setter method
        """
        self.task.set_prev_state(Task.STATUS_CHOICES[1][0])
        self.assertEqual(self.task.get_prev_state(), Task.STATUS_CHOICES[1][0])

    def test_handle_priority_on_adding_new_task(self):
        """
        A new task with same priotiry is added this should result in inrease of
        all the prev continious tasks priority
        """
        # Creating a new task with priority 1
        new_task = Task(title="Task with priority 1 Again", priority=1, user=self.user)
        new_task.save()
        # get new task from database
        new_task = Task.objects.get(id=new_task.id)
        self.assertEqual(new_task.priority, 1)
        # get prev task from database
        prev_task = Task.objects.get(id=self.task.id)
        self.assertEqual(prev_task.priority, 2)

    def test_handle_priority_on_updating_prev_task(self):
        """
        A new task with priority 2 is added and prev tasks priority is updated to 2
        this should result in new task priority increased to 3
        """
        # Creating a new task with priority 1
        new_task = Task(title="Task with priority 2", priority=2, user=self.user)
        new_task.save()
        # update prev_task
        prev_task = Task.objects.get(id=self.task.id)
        prev_task.priority = 2
        prev_task.save()
        # get new task from database
        new_task = Task.objects.get(id=new_task.id)
        self.assertEqual(new_task.priority, 3)
        # get prev task from database
        prev_task = Task.objects.get(id=self.task.id)
        self.assertEqual(prev_task.priority, 2)

    def test_handle_priority_on_adding_new_task_of_diff_user(self):
        """
        A new task with priority same as prev task is added but this time
        it is associated with a different user, hence no changes should be made
        on prev task
        """
        # Creating a new task with priority 1 and a new user
        new_user = User(
            username="user2", email="user2@django.com", password="welcome@123"
        )
        new_user.save()
        new_task = Task(
            title="Task with priority 1 Again and different user",
            priority=1,
            user=new_user,
        )
        new_task.save()
        # get new task from database
        new_task = Task.objects.get(id=new_task.id)
        self.assertEqual(new_task.priority, 1)
        # get prev task from database
        prev_task = Task.objects.get(id=self.task.id)
        self.assertEqual(prev_task.priority, 1)

    def test_handle_priority_on_updating_completed_task(self):
        """
        A new task is created with priority 2 and now its updated to priorty 1 and
        completed to true, this should not effect the priority of prev task
        """
        # Creating a new task with priority 1
        new_task = Task(title="Task with priority 2", priority=2, user=self.user)
        new_task.save()
        # updating new task
        new_task.priority = 1
        new_task.completed = True
        new_task.save()
        # get new task from database
        new_task = Task.objects.get(id=new_task.id)
        self.assertEqual(new_task.priority, 1)
        # get prev task from database
        prev_task = Task.objects.get(id=self.task.id)
        self.assertEqual(prev_task.priority, 1)


class HistoryTest(TestCase):
    def setUp(self):
        self.user = User(
            username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman"
        )
        self.user.save()

    def test_str(self):
        """
        It should print task title with change of status
        """
        task = Task(title="Task with priority 1", priority=1, user=self.user)
        task.save()
        previous_status = task.status
        # update task status
        task.status = Task.STATUS_CHOICES[1][0]
        task.save()
        # fetch lastest task object
        task = Task.objects.get(id=task.id)
        new_status = task.status
        history = History.objects.filter(task=task).first()
        self.assertEqual(
            str(history),
            f"{task.title} changed from '{previous_status}' to '{new_status}'",
        )

    def test_handle_history_on_no_status_change(self):
        """
        If there is no status change a new history object shouldnt be formed
        """
        task = Task(title="Task with priority 1", priority=1, user=self.user)
        task.save()
        # update task status
        task.title = "New title of task 1"
        task.save()
        # fetch lastest task object
        task = Task.objects.get(id=task.id)
        history = History.objects.filter(task=task)
        self.assertEqual(history.count(), 0)

    def test_handle_history_on_status_change(self):
        """
        It should create a new history object with prev and new status correctly
        """
        task = Task(title="Task with priority 1", priority=1, user=self.user)
        task.save()
        previous_status = task.status
        # update task status
        task.status = Task.STATUS_CHOICES[1][0]
        task.save()
        # fetch lastest task object
        task = Task.objects.get(id=task.id)
        new_status = task.status
        history = History.objects.filter(task=task)
        self.assertEqual(history.count(), 1)
        self.assertEqual(
            str(history.first()),
            f"{task.title} changed from '{previous_status}' to '{new_status}'",
        )


class ScheduleTest(TestCase):
    def setUp(self):
        self.user = User(
            username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman"
        )
        self.user.save()
        self.schedule = Schedule(user=self.user, time="02:00:00")
        self.schedule.save()

    def test_str(self):
        """
        It should print the daily schedule of the user
        """
        self.assertEqual(str(self.schedule), f"Schedule for 02:00:00 daily")
