import time
from django.contrib.auth.models import User
from django.core.mail import send_mail
from tasks.models import Task
from datetime import timedelta

from celery.decorators import periodic_task
from task_manager.celery import app


@periodic_task(run_every=timedelta(seconds=10))
def send_email_reminder():
    print("Statring process")
    for user in User.objects.all():
        pending_qs = Task.objects.filter(deleted=False, completed=False, user=user)
        email_content = f"You have {pending_qs.count()} Pending Tasks"
        send_mail(
            "Pending Tasks from Task Manager",
            email_content,
            "task@task_manager.org",
            [user.email],
        )
        print(f"Completed Processing {user.id}")
