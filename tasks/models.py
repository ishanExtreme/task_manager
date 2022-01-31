from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver  # decorator
from django.db import transaction


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    priority = models.IntegerField()

    def __str__(self):
        return self.title


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
