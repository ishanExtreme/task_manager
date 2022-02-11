from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction


class Task(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "PENDING"),
        ("IN_PROGRESS", "IN_PROGRESS"),
        ("COMPLETED", "COMPLETED"),
        ("CANCELLED", "CANCELLED"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # private variable
        # Case 1: In creating new Task __init__ is called with status
        # so prev_state will always be equal to new state in this case
        # Case 2: For updating a task its instance is created which populate
        # prev field with current status and after filling form status is changed
        # but prev state will contain the right value as init is not called again
        self._prev_state = self.status

    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    priority = models.IntegerField()
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )

    def __str__(self):
        return self.title

    def set_prev_state(self, state):
        self._prev_state = state

    def get_prev_state(self):
        return self._prev_state


# Flow=> when object is created for first time exclude is not required as it is a
# pre save signal but when updation is called exclude is required as the current
# id is already present in the database
@receiver(pre_save, sender=Task)  # decorator to make it the reciever function
def handle_priority(sender, instance, *args, **kwargs):
    """
    Called before saving the Task model to handle the priority logic
    sender-> Task model
    instance-> Task model object
    """
    # no need to update priorities if user updates task to complete and
    # also changes the priority
    # TODO: implement logic to not query if priority is not updated for example
    # if only title/disc is updated and priority is unchanged
    if instance.completed == False:

        # print("***********************************************************")
        # print(instance.__dict__)
        # print("***********************************************************")
        inc_priority = instance.priority
        # get all tasks with priority greater than equal to current priority
        tasks = (
            Task.objects.filter(
                deleted=False,
                user=instance.user,
                completed=False,
                priority__gte=inc_priority,
            )
            .exclude(id=instance.id)  # exclude current object
            # lock the rows until transaction is complete
            .select_for_update()
            .order_by("priority")
        )

        # atomic transaction so that all increment takes place if one of them fails
        # whole increment roll backs to original format
        with transaction.atomic():
            updated_tasks = []
            for task in tasks:
                if task.priority == inc_priority:
                    task.priority += 1
                    updated_tasks.append(task)
                    inc_priority += 1
                else:
                    break
            if updated_tasks:
                # on bulk update save method is not called hence signal is not retriggered
                Task.objects.bulk_update(
                    updated_tasks, fields=["priority"], batch_size=1000
                )


class History(models.Model):
    # related to task object one to many relation
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    previous_status = models.CharField(max_length=100, choices=Task.STATUS_CHOICES)
    new_status = models.CharField(max_length=100, choices=Task.STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.title} changed from '{self.previous_status}' to '{self.new_status}'"


# We take out the prev_state private field and create a new history object
@receiver(post_save, sender=Task)
def handle_history(sender, instance, created, *args, **kwargs):

    # only create new history object is status is being changed
    if instance.get_prev_state() != instance.status:
        history = History(
            task=instance,
            previous_status=instance.get_prev_state(),
            new_status=instance.status,
        )
        history.save()


class Schedule(models.Model):

    time = models.TimeField(default="00:00:00")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Schedule for {self.hours}:{self.minutes} daily"
