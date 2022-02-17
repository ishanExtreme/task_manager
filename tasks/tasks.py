from django.contrib.auth.models import User
from django.core.mail import send_mail
from tasks.models import Task, History, Schedule
from datetime import timedelta, datetime

from celery.decorators import periodic_task
from celery import shared_task
from celery.schedules import crontab
from task_manager.celery import app
from django.utils.timezone import make_aware
from django.db.models import Q


def send_email_util(user_id):
    user = None
    try:
        user = User.objects.get(id=user_id)
    # CASE:User gets deleted
    # before worker start executing the email sending for that user
    except:
        print("User deleted from database")
        return

    all_qs = Task.objects.filter(deleted=False, user=user)
    pending = all_qs.filter(status=Task.STATUS_CHOICES[0][0]).count()
    in_progress = all_qs.filter(status=Task.STATUS_CHOICES[1][0]).count()
    completed = all_qs.filter(status=Task.STATUS_CHOICES[2][0]).count()

    email_content = f"""Hi {user.get_username()}.
    Your task report is shown below:
    Pending:{pending}
    INProgress:{in_progress}
    Completed:{completed}
    """

    send_mail(
        "Task Report from Task Manager",
        email_content,
        "task@task_manager.org",
        [user.email],
    )


# Flow=>
# Step1: get all the users who have schedule object associated with them
# Step2: from those users filter the users to whom email is not sent within 24 hrs
# As we have to send one email daily so we will check if there are any emails send
# to that user in 24 hrs if not we keep them
# Step3: filter out users who have schedule time less than the current time. This handles
# every case of workder stop responding for any amount of time
# Step4: After sending them mail update the prev_sent time
# On updating the time if cuurent time is more than updated time
# a mail is sent irrespective of current time from next day
# it is sent at correct timings
# TODO: Limit user to update schedule a certain number of times a day
# to prevent email overloading on worker
@periodic_task(run_every=timedelta(seconds=60))
def schedule_worker():
    curr_time = make_aware(datetime.now())
    # Get all users with defined schedule
    user_query = User.objects.filter(
        schedule__isnull=False,
    )

    # print(f"Step-1:{user_query}")
    user_query = user_query.filter(
        Q(schedule__prev_sent_time__lte=curr_time - timedelta(days=1))
        | Q(schedule__prev_sent_time__isnull=True)
    ).filter(schedule__time__lte=curr_time.time())
    # print(f"Step-2,3:{user_query}")

    for user in user_query:
        user_schedule = user.schedule
        # Here current time is not used bcz if our worker doesnt reponds for
        # 2 hrs(say) and our schedule mail of 12am is sent at 2am then next day
        # it is again sent at 2am.
        user_schedule.prev_sent_time = curr_time.replace(
            hour=user_schedule.time.hour, minute=user_schedule.time.minute
        )
        # its right place is after sending email. But this will add
        # extra edge cases for simplicity saving it here
        user_schedule.save()
        send_email_util(user.id)
