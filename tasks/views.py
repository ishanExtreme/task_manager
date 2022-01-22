from django.http import HttpResponseRedirect
from django.shortcuts import render
from tasks.models import Task


def add_task(request):
    """
    Add a new task to the model
    """
    task_value = request.GET.get("task")
    Task(title=task_value).save()
    return HttpResponseRedirect("/tasks")


def display_tasks(request):
    """
    Display incomplete tasks and searches tasks
    """
    search_term = request.GET.get("search")
    # query returns all the tasks which are not deleted and not marked complete
    tasks = Task.objects.filter(deleted=False).filter(completed=False)
    if search_term:
        # case insensitive filter to display search terms
        tasks = tasks.filter(title__icontains=search_term)

    return render(request, "tasks.html", {"tasks": tasks})


def delete_task(request, index):
    """
    Delete task from the list. Takes primary key of the task as parameter
    """
    # soft delete the task
    Task.objects.filter(id=index).update(deleted=True)
    return HttpResponseRedirect("/tasks")


def mark_complete(request, index):
    """
    Marks task as complete by removing it from taks list and
    adding it to complete list. Takes primary key of the task as parameter
    """
    Task.objects.filter(id=index).update(completed=True)
    return HttpResponseRedirect("/tasks")


def display_completed_tasks(request):
    """
    Displays completed tasks
    """
    search_term = request.GET.get("search")
    # query returns all the tasks which are not deleted and marked complete
    tasks = Task.objects.filter(deleted=False).filter(completed=True)
    if search_term:
        # case insensitive filter to display search terms
        tasks = tasks.filter(title__icontains=search_term)
    return render(request, "completed.html", {"tasks": tasks})


def display_all_tasks(request):
    """
    Displays both pending and completed tasks
    """
    # query returns all the tasks which are not deleted and not completed
    tasks = Task.objects.filter(deleted=False).filter(completed=False)
    # query returns all the tasks which are not deleted and marked complete
    complete = Task.objects.filter(deleted=False).filter(completed=True)
    return render(request, "all_task.html", {"complete": complete, "pending": tasks})
