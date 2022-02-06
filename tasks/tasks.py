from django.contrib.auth.models import User
from django.core.mail import send_mail
from tasks.models import Task, History, Schedule
from datetime import timedelta, datetime

from celery.decorators import periodic_task
from celery import shared_task
from celery.schedules import crontab
from task_manager.celery import app


def send_email_util(user):

    pending_qs = Task.objects.filter(deleted=False, completed=False, user=user)
    email_content = f"""Hi {user.get_username()}.

    You have {pending_qs.count()} tasks pending.
    Here is the full report for your pending tasks:

    """
    for task in pending_qs:
        task_history = History.objects.filter(task=task)
        for history in task_history:
            email_content += f"{history}\n"

    send_mail(
        "Task Report from Task Manager",
        email_content,
        "task@task_manager.org",
        [user.email],
    )


# for production envioroment where email sending can fail
# default_retry_delay=1 * 60, max_retries=3
@app.task
def send_email_async(user_id):

    user = None
    try:
        user = User.objects.get(id=user_id)
    # CASE:User gets deleted
    # before worker start executing the email sending for that user
    except:
        print("User deleted from database")
        return
    send_email_util(user)
    # after succesfully sending email set email send to true
    Schedule.objects.filter(user=user).update(email_sent=True)


# Call every minute
# Loop over all users
# If user have schedule settings associated with it
#   send email when their time matches with current time
# else
#   continue
# ----Case1----: emails are checked with +-3 minutes accuracy for this send field is used
# to not send the email again
# ----Case2----: For email system to work again next day schedule a cron job which starts
# at 12 am every day and sets all sent_email to false
# ----Case3----: If earlier schedule was at 2PM and user reschedules it to 1PM at
# 12PM(current time) current logic can handle such update
#  ----Case4----: If earlier schedule was 1PM and user updates schedule to 3PM at
# 2PM(current time) this will not send email again to user at 3 as email_sent will be
# false for this every time user updates schedule set email_sent to true
@periodic_task(run_every=timedelta(seconds=60))
def schedule_worker():
    curr_time = datetime.now()
    for user in User.objects.all():
        user_schedule = Schedule.objects.filter(user=user)
        if not user_schedule.exists():
            continue
        user_schedule = user_schedule.first()
        schedule = curr_time.replace(
            hour=user_schedule.hours, minute=user_schedule.minutes
        )
        # emails are sent with minutes accuracy of +- 3 minutes
        if (
            abs(curr_time - schedule) <= timedelta(minutes=3)
            and not user_schedule.email_sent
        ):
            send_email_async.delay(user.id)


# This crontab methods as given in official docs
# doesn't work
# @app.on_after_finalize.connect
# def reset_sheduler(sender, **kwargs):

#     sender.conf.beat_schedule["reset_scheduler"] = {
#         "task": "tasks.reset_util",
#         "schedule": crontab(minute="*/1"),
#     }
#     # (
#     #     # execute daily at midnight
#     #     crontab(minute="*/1"),
#     #     reset_util(),
#     # )


# execute daily at midnight
app.conf.beat_schedule = {
    "reset_scheduler": {
        "task": "tasks.reset_util",
        "schedule": crontab(minute=0, hour=0),
    },
}


@app.task
def reset_util():
    print("Started Reset")
    Schedule.objects.all().update(email_sent=False)
