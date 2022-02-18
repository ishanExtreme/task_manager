from django.test import TestCase
from django.contrib.auth.models import User
from ..tasks import send_email_util, schedule_worker
from django.core import mail
from ..models import Schedule, Task
from datetime import timedelta, datetime
from django.utils.timezone import make_aware


class CeleryTasksTest(TestCase):
    def setUp(self):
        self.user = User(username="ishan", email="bruce@wayne.org")
        self.user.set_password("welcome@123")
        self.user.save()
        task1 = Task(
            title="Task with title 1",
            priority=1,
            user=self.user,
            completed=False,
            status=Task.STATUS_CHOICES[0][0],
        )
        task1.save()
        task2 = Task(
            title="Task with title 2",
            priority=1,
            user=self.user,
            completed=True,
            status=Task.STATUS_CHOICES[1][0],
        )
        task2.save()
        task3 = Task(
            title="Task with title 3",
            priority=1,
            user=self.user,
            completed=True,
            status=Task.STATUS_CHOICES[2][0],
        )
        task3.save()
        self.curr_dtime = make_aware(datetime.now())

    def test_send_email_util(self):
        send_email_util(self.user.id)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Task Report from Task Manager")
        email_content = f"Hi {self.user.get_username()}.\nYour task report is shown below:\nPending:1\nINProgress:1\nCompleted:1"
        self.assertEqual(mail.outbox[0].body, email_content)
        self.assertEqual(mail.outbox[0].from_email, "task@task_manager.org")
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    def test_send_schedule_email_if_no_prev_sent_defined(self):
        """
        Fresh user we are sending schedule to him/her for first time
        """
        # schedule for 1 min before curr time
        Schedule(
            time=(self.curr_dtime - timedelta(minutes=2)).time(), user=self.user
        ).save()
        schedule_worker()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    def test_send_schedule_email_if_curr_time_is_less_then_schedule(self):
        """
        no email is send if curr time is smaller then scheduled time
        """
        # schedule is 1 hr after curr time
        Schedule(
            time=(self.curr_dtime + timedelta(hours=1)).time(), user=self.user
        ).save()
        schedule_worker()
        self.assertEqual(len(mail.outbox), 0)

    # Note this test may fail if tested at exact 12 am (00:00) to 12:30 am
    # Key point  to note is if worker crashed at 11.20 pm and email
    # schedule is 11.22 and worker woke up at 00:00 it will not send email
    # to this person as 00 < 23
    def test_send_schedule_email_if_curr_time_is_more_then_schedule(self):
        """
        scenario where worker may fail for a long period of time
        so email should be sent as soon as worker is live again
        """
        # schedule was 30 mins before curr time
        Schedule(
            time=(self.curr_dtime - timedelta(minutes=30)).time(), user=self.user
        ).save()
        schedule_worker()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    def test_send_schedule_email_if_email_was_already_sent_in_24_hrs(self):
        """
        scenario where an email is sent succesfully and is not sent again in
        24 hrs
        """
        # schedule was 30 mins before curr time
        # and an email was already sent
        time = (self.curr_dtime - timedelta(minutes=30)).time()
        Schedule(
            time=time,
            user=self.user,
            prev_sent_time=self.curr_dtime.replace(hour=time.hour, minute=time.minute),
        ).save()
        schedule_worker()
        self.assertEqual(len(mail.outbox), 0)

    def test_email_is_send_succesfully_after_24_hrs(self):
        """
        Scenario where email was sent succesfully yesterday and should sent an
        email again today at scheduled time
        """
        time = self.curr_dtime.time()
        # email sent yesterday as indeicated by prev sent time
        Schedule(
            time=time,
            user=self.user,
            prev_sent_time=self.curr_dtime - timedelta(days=1),
        ).save()
        schedule_worker()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
